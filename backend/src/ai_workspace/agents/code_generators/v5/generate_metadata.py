from typing import List, Literal

from pydantic import BaseModel, Field
from langsmith import Client
from langgraph.graph import END, START, StateGraph

from ai_workspace.core import LLMConfiguration
from ai_workspace.utils import validate_llm_output, save_graph_visualization
from langchain.chat_models import init_chat_model

from .classification_question_topic import (
    app as topic_classification_graph,
    State as TopicInputState,
)

client = Client()

cfg = LLMConfiguration()
base_llm = init_chat_model(model=cfg.base_model, model_provider=cfg.model_provider)


class QuestionData(BaseModel):
    question: str
    title: str = Field(..., description="A concise title summarizing the question")
    isAdaptive: Literal["True", "False"] = Field(
        ...,
        description=(
            "Whether the question is adaptive (requires computation and a backend) "
            "or non-adaptive (e.g., multiple choice)."
        ),
    )


class MetadataInput(BaseModel):
    question: str
    title: str = ""
    topics: List[str] = Field(default=[])
    isAdaptive: Literal["True", "False"] = "False"


def base_question_classification(state: MetadataInput):
    metadata_prompt = client.pull_prompt("base_metadata")
    chain = metadata_prompt | base_llm.with_structured_output(QuestionData)
    result: QuestionData = validate_llm_output(
        chain.invoke({"question": state.question}), QuestionData
    )
    return {
        "title": result.title,
        "isAdaptive": result.isAdaptive,
    }  # type: ignore


def topic_classification(state: MetadataInput):
    result: TopicInputState = validate_llm_output(
        topic_classification_graph.invoke(
            input=TopicInputState(question=state.question)
        ),
        TopicInputState,
    )
    return {"topics": result.topics}


graph = StateGraph(MetadataInput)
graph.add_node("base_question_classificaton", base_question_classification)
graph.add_node("topic_classification", topic_classification)

graph.add_edge(START, "base_question_classificaton")
graph.add_edge(START, "topic_classification")
graph.add_edge("base_question_classificaton", END)
graph.add_edge("topic_classification", END)

compiled_graph = graph.compile()


def main():
    save_graph_visualization(
        compiled_graph,  # type: ignore
        filename="question_metadata.png",
        base_path=r"ai_workspace\agents\code_generators\v5\graphs",
    )
    question = "A car is traveling along a straight road at 60 mph; calculate distance after 4 hours"
    input_state = MetadataInput(question=question)  # type: ignore
    for chunk in compiled_graph.stream(input_state, stream_mode="updates"):
        print(chunk)


if __name__ == "__main__":
    main()
