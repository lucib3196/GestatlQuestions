from .extract_question_image import app as question_extraction
from ai_workspace.models import Question
from pydantic import BaseModel
from typing import List
from ai_workspace.models.payloads import Question
from langgraph.graph import END, START, StateGraph
from typing import Optional
import asyncio

from ai_workspace.agents.code_generators.v4.qmeta import (
    compiled_graph as codegen_interface,
    CodeGenInput,
    OutputState,
)


class InputState(BaseModel):
    image_paths: List[str]


class IntermediateState(BaseModel):
    questions: Optional[List[Question]] = None
    code_results: List[OutputState] = []


async def extract_question(state: InputState) -> IntermediateState:
    result = await question_extraction.ainvoke({"image_paths": state.image_paths})  # type: ignore
    return {"questions": result.get("questions").questions}  # type: ignore


async def generate_code(state: IntermediateState) -> IntermediateState:
    tasks = [
        codegen_interface.ainvoke(CodeGenInput(question_payload=q, initial_metadata={}))
        for q in state.questions or []
    ]
    results = await asyncio.gather(*tasks)
    return {"code_results": results}  # type: ignore


graph = StateGraph(
    IntermediateState, input_schema=InputState, output_schema=IntermediateState
)
graph.add_node("extract_question", extract_question)  # type: ignore
graph.add_node("generate_code", generate_code)  # type: ignore


graph.add_edge(START, "extract_question")
graph.add_edge("extract_question", "generate_code")
graph.add_edge("generate_code", END)

app = graph.compile()

if __name__ == "__main__":

    async def main():
        from pathlib import Path
        import json, re
        from ai_workspace.utils import to_serializable

        # Combine multiple questions into one text
        image_paths = [r"images\mass_block.png"]

        # Run the app
        results = await app.ainvoke(
            InputState(image_paths=image_paths),
        )  # type: ignore

        # Parse to your Pydantic state
        state = IntermediateState.model_validate(results)

        # Normalize code_results to a list
        raw_list = state.code_results or []
        code_results = raw_list if isinstance(raw_list, list) else [raw_list]

        # Output directory
        out_dir = Path("ai_workspace/agents/code_generators/v5/complete_outputs")
        out_dir.mkdir(parents=True, exist_ok=True)

        # Helper to make a filesystem-safe filename
        def safe_name(name: str, fallback: str) -> str:
            name = name or fallback
            name = re.sub(r'[<>:"/\\|?*\n\r\t]', "_", name).strip()
            name = re.sub(r"_+", "_", name)
            return name[:120] or fallback

        # Save one file per code_result
        for i, cr in enumerate(code_results, start=1):
            title = getattr(getattr(cr, "qmeta", None), "title", "") or f"output_{i}"
            fname = f"{safe_name(title, f'output_{i}')}.json"
            out_path = out_dir / fname

            # Serialize just this code_result (not the whole results blob)
            out_path.write_text(
                json.dumps(to_serializable(cr), indent=4, ensure_ascii=False),
                encoding="utf-8",
            )
            print(f"Saved {out_path}")

        # Optional: also save the full results once
        full_path = out_dir / "_full_results.json"
        full_path.write_text(
            json.dumps(to_serializable(results), indent=4, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"Saved {full_path}")

    asyncio.run(main())
