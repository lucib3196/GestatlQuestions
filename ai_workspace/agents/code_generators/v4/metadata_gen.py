from typing import List, Literal, Optional
from pydantic import BaseModel, Field

from langchain import hub
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.pregel import RetryPolicy  # type: ignore

from ai_workspace.utils import parse_structured, save_graph_visualization
from ai_workspace.agents.question_topic_classification_agent.question_topic_classification_agent import (
    app as topic_classifier,
)
from ai_workspace.agents.course_classification_agent.course_classification_agent import (
    app as course_classification,
)
from ai_workspace.agents.course_classification_agent.course_classification_agent import (
    CourseClassification,
)


# Constants
FASTLLM = "gpt-4o-mini"
fast_llm = ChatOpenAI(model=FASTLLM)


class MetadataInput(BaseModel):
    question: str


class MetadataState(BaseModel):
    question: str = Field(default="")
    title: str = Field(default="")
    topic: List[str] = Field(default=[])
    relevantCourses: List[str] = Field(default=[])
    isAdaptive: Optional[Literal["True", "False"]] = None


# Structure Base Model for LLM response
class QuestionMetadata(BaseModel):
    title: str = Field(..., description="A consise title summarizing the question ")
    isAdaptive: Literal["True", "False"] = Field(
        ...,
        description="Whether the question is adaptive (requires computation and a backend) or non-adaptive (e.g., multiple choice).",
    )


def classify_question(state: MetadataInput) -> MetadataState:
    metadata_prompt = hub.pull("gestalt_metadata")
    chain = metadata_prompt | fast_llm.with_structured_output(
        QuestionMetadata, include_raw=True
    )
    result = chain.invoke({"question": state.question})
    ai_message = result["raw"]
    question_metadata = parse_structured(QuestionMetadata, ai_message)
    return {
        "title": question_metadata.title,
        "isAdaptive": question_metadata.isAdaptive,
    }  # type: ignore


def classify_question_topic(state: MetadataInput) -> MetadataState:
    topics = topic_classifier.invoke({"question": state.question})  # type: ignore
    return {"topic": topics.get("topic_classification_result").topics}  # type: ignore


def classify_question_courses(state: MetadataInput) -> MetadataState:
    relevant_courses = course_classification.invoke({"question": state.question})  # type: ignore

    return {"relevant_courses": relevant_courses.get("generation", CourseClassification(course_id=[])).course_id}  # type: ignore


graph = StateGraph(MetadataState, input_schema=MetadataInput)
nodes = [
    ("classify_question_topic", classify_question_topic),
    ("generate_metadata_legacy", classify_question),
    ("classify_question_courses", classify_question_courses),
]
for name, func in nodes:
    graph.add_node(name, func, retry=RetryPolicy(max_attempts=1))  # type: ignore

graph.add_edge(START, "classify_question_topic")
graph.add_edge(START, "classify_question_courses")
graph.add_edge(START, "generate_metadata_legacy")

graph.add_edge("classify_question_topic", END)
graph.add_edge("classify_question_courses", END)
graph.add_edge("generate_metadata_legacy", END)

compiled_graph = graph.compile()


def main():
    save_graph_visualization(
        compiled_graph,  # type: ignore
        filename="QuestionMetadata.png",
        base_path=r"ai_workspace/agents/code_generator/v4/graphs",
    )
    question = "A car is traveling along a straight road at 60 mph; calculate distance after 4 hours"
    input_state = MetadataInput(question=question, initial_metadata=None)  # type: ignore
    for chunk in compiled_graph.stream(input_state, stream_mode="updates"):
        print(chunk)


if __name__ == "__main__":
    main()
