from ai_workspace.models import Question
from pydantic import BaseModel
from typing import List
from ai_workspace.models.payloads import Question
from api.core.logging import logger
from langsmith import Client
from langgraph.graph import END, START, StateGraph
from langchain.chat_models import init_chat_model
from typing import Optional
from ai_workspace.utils import validate_llm_output

client = Client()
extract_question_prompt = client.pull_prompt("extract-all-questions-text")


# Constants
fast_llm = "gpt-5-mini"
fast_model = init_chat_model("gpt-5-mini", model_provider="openai")


class State(BaseModel):
    text: str
    questions: Optional[List[Question]] = None


class QuestionClassification(BaseModel):
    questions: List[Question]


async def classify_question(state: State):
    structured_llm = fast_model.with_structured_output(QuestionClassification)
    chain = extract_question_prompt | structured_llm
    results:QuestionClassification = validate_llm_output(
        await chain.ainvoke({"question": state.text}), QuestionClassification
    )
    return {"questions": results.questions}


graph = StateGraph(State)
graph.add_node("classify_question", classify_question)  # type: ignore

graph.add_edge(START, "classify_question")
graph.add_edge("classify_question", END)

app = graph.compile()


if __name__ == "__main__":
    import asyncio
    import json
    import os
    from datetime import datetime
    from pathlib import Path
    from typing import Any, Dict, List

    from ai_workspace.utils import (
        save_graph_visualization,
        to_serializable,
    )  # noqa: E402

    OUTPUT_DIR = Path("ai_workspace/agents/code_generators/v5/outputs")
    GRAPH_DIR = Path("ai_workspace/agents/code_generators/v5/graphs")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)

    TEST_CASES = [
        {
            "id": "ball_d_equals_vt_with_answer",
            "text": (
                "A ball travels at a constant speed of 10 m/s for a total time of 20 s. "
                "How much distance did the ball cover? The correct answer for the question "
                "is given by the equation d = v t, so for this question the answer will be 200 m."
            ),
        },
        {
            "id": "car_distance_parameters_only",
            "text": (
                "A car travels at speed v = 20 m/s for time t = 5 s. "
                "Compute the distance traveled."
            ),
        },
        {
            "id": "incline_symbols_units",
            "text": (
                "A block of mass m = 2 kg is on an incline of 30°. "
                "The friction coefficient is μ = 0.2. Use g = 9.81 m/s^2. "
                "Find the acceleration."
            ),
        },
    ]

    async def run_case(case: Dict[str, str]) -> Dict[str, Any]:
        """Stream one test case and return all chunks."""
        case_id = case["id"]
        prompt = {"text": case["text"]}

        logger.info(f"[{case_id}] starting stream")
        chunks: List[Any] = []
        try:
            async for chunk in app.astream(prompt, stream_mode="values"):  # type: ignore
                # Optional: log minimal info to avoid noisy output
                logger.debug(f"[{case_id}] chunk: {chunk}")
                chunks.append(chunk)
        except Exception as e:
            logger.exception(f"[{case_id}] stream failed: {e}")

        # Save per-case JSON
        per_case_path = OUTPUT_DIR / f"{case_id}.json"
        with per_case_path.open("w", encoding="utf-8") as f:
            json.dump(to_serializable(chunks), f, ensure_ascii=False, indent=2)
        logger.info(f"[{case_id}] wrote {per_case_path}")

        return {
            "id": case_id,
            "input": case["text"],
            "chunks": chunks,
        }

    async def main():
        # Optional: one-time graph visualization
        save_graph_visualization(  # type: ignore
            app,  # type: ignore
            filename="Question Extraction Text.png",
            base_path=str(GRAPH_DIR),
        )

        all_results: List[Dict[str, Any]] = []

        # Run sequentially to keep logs/results easy to read.
        for case in TEST_CASES:
            result = await run_case(case)
            all_results.append(result)

        # Write combined file with timestamp
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        combined_path = OUTPUT_DIR / f"extract_question_text_all_{ts}.json"
        with combined_path.open("w", encoding="utf-8") as f:
            json.dump(to_serializable(all_results), f, ensure_ascii=False, indent=2)
        logger.info(f"[combined] wrote {combined_path}")

    asyncio.run(main())
