from src.ai_workspace.agents.code_generators.v4_5.extract_question_image import (
    InputState as ImageUploadState,
    IntermediateState as FinalState,
    app as image_upload_graph,
)

from .gestalt_generator import (
    app as gestalt_generator,
    CodeGen,
    FinalState as CodeGenFinal,
)
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel
from src.ai_workspace.models import Question
from typing import List
from src.ai_workspace.utils import validate_llm_output
import asyncio


class State(BaseModel):
    image_paths: List[str]
    questions: List[Question] = []
    gestalt_code: List[CodeGenFinal] = []


async def extract_question(state: State):
    result = await image_upload_graph.ainvoke(
        ImageUploadState(image_paths=state.image_paths)
    )
    
    print("This is the result\n\n\n", result, type(result))
    result = validate_llm_output(result, FinalState)
    return {"questions": result.questions}


async def generate_code(state: State) -> State:
    tasks = [
        gestalt_generator.ainvoke(
            CodeGen(
                question_payload=q,
            )
        )
        for q in state.questions or []
    ]
    results = await asyncio.gather(*tasks)
    return {"gestalt_code": results}  # type: ignore


graph = StateGraph(State)
graph.add_node("extract_question", extract_question)  # type: ignore
graph.add_node("generate_code", generate_code)  # type: ignore


graph.add_edge(START, "extract_question")
graph.add_edge("extract_question", "generate_code")
graph.add_edge("generate_code", END)

app = graph.compile()
