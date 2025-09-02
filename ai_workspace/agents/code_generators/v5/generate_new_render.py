from typing import List, Optional

from langgraph.graph import END, START, StateGraph
from langsmith import Client
from langchain.chat_models import init_chat_model
from pydantic import BaseModel

from ai_workspace.models.payloads import QuestionBase
from ai_workspace.core.config import LLMConfiguration
from ai_workspace.utils import validate_llm_output


# --- Configuration and Model Setup ---
config = LLMConfiguration()
fast_model = config.fast_model

base_llm = init_chat_model(
    model=config.base_model,
    model_provider=config.model_provider,
)

langsmith_client = Client()
prompt = langsmith_client.pull_prompt("new_question_render")


# --- Pydantic Models ---
class Response(BaseModel):
    response: List[QuestionBase] = []


class State(BaseModel):
    question_html: str
    solution_html: str
    new_render: List[QuestionBase] = []


# --- Node Function ---
def generate_render(state: State):
    chain = prompt | base_llm.with_structured_output(Response)

    result: Response = validate_llm_output(
        chain.invoke(
            {
                "question": state.question_html,
                "solution": state.solution_html,
            }
        ),
        Response,
    )

    return {"new_render": result.response}


# --- Graph Definition ---
graph = StateGraph(State)
graph.add_node("generate_render", generate_render)
graph.add_edge(START, "generate_render")
graph.add_edge("generate_render", END)

app = graph.compile()
