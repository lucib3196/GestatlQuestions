# ======================
# Standard library
# ======================
from typing import Optional

# ======================
# Third-party libraries
# ======================
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, START, StateGraph
from langsmith import Client
from pydantic import BaseModel
from api.core.logging import logger

# ======================
# Local application
# ======================
from .initializer import init_generation
from ai_workspace.models import CodeResponse
from ai_workspace.utils import (
    save_graph_visualization,
    inject_message,
    validate_llm_output,
)
from ai_workspace.retrievers import SemanticExamplesCSV


# ======================
# Initialization
# ======================
client = Client()

resources = init_generation(
    name="question html",
    column_names=("question", "question.html"),
)

prompt_base = "question_html_template"
fast_llm = resources.fast_llm
base_llm = resources.base_llm


if isinstance(resources.q_retriver, SemanticExamplesCSV):
    q_retriever = resources.q_retriver
else:
    raise TypeError("Expected SemanticExamplesCSV")


class State(BaseModel):
    question: str
    isAdaptive: bool = True
    question_html: str = ""


def generate_question_html(state: State):
    base_prompt = client.pull_prompt(prompt_base)

    q_retriever.set_filter({"isAdaptive": state.isAdaptive})
    prompt_result = q_retriever.format_template(
        query=state.question, k=3, base_template=base_prompt
    )
    if isinstance(prompt_result, str):
        prompt: ChatPromptTemplate = ChatPromptTemplate.from_template(prompt_result)
    else:
        prompt: ChatPromptTemplate = prompt_result

    messages = prompt.format_prompt(question=state.question).to_messages()

    chain = base_llm.with_structured_output(CodeResponse)

    result: CodeResponse = validate_llm_output(chain.invoke(messages), CodeResponse)
    return {"question_html": result.code}  # type: ignore


workflow = StateGraph(State)
workflow.add_node("generate_question_html", generate_question_html)  # type: ignore


workflow.add_edge(START, "generate_question_html")
workflow.add_edge("generate_question_html", END)
app = workflow.compile()

if __name__ == "__main__":
    save_graph_visualization(
        app,  # type: ignore
        "solution_html.png",
        base_path=r"ai_workspace\agents\code_generators\v5\graphs",
    )

    async def test():
        t_inputs = [
            {
                "question": "A car is traveling along a straight road at a speed of 20 m/s. It sees a stop sign 50 m ahead and applies the brakes, coming to a complete stop just as it reaches the sign. What is the car's constant acceleration during this process? Show your calculations.",
                "isAdaptive": True,
            }
        ]
        for t in t_inputs:
            async for chunk in app.astream(State(**t), stream_mode="updates"):
                print(chunk)

    import asyncio

    asyncio.run(test())
