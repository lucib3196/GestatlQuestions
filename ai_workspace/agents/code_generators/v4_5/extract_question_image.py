from ai_workspace.image_processing import ImageLLMProcessor
from ai_workspace.models import Question
from pydantic import BaseModel
from typing import List
from ai_workspace.models.payloads import Question
from backend_api.core.logging import logger
from langsmith import Client
from langgraph.graph import END, START, StateGraph

client = Client()
extract_question_prompt = client.pull_prompt("extract-all-questions")
extract_question_prompt = extract_question_prompt.messages[
    0
].content  # Extract just the system prompt
# Constants
fast_llm = "gpt-5-mini"


# Define extraction Schema
class ExtractedQuestions(BaseModel):
    questions: List[Question]


class InputState(BaseModel):
    image_paths: List[str]


class IntermediateState(BaseModel):
    questions: List[Question]


async def extract_question(state: InputState) -> IntermediateState:
    extractor = ImageLLMProcessor(
        prompt=extract_question_prompt, schema=ExtractedQuestions, model=fast_llm
    )
    results = await extractor.send_arequest(state.image_paths)

    return {"questions": results}  # type: ignore


graph = StateGraph(
    state_schema=IntermediateState,
    input_schema=InputState,
    output_schema=IntermediateState,
)
graph.add_node("extract_question", extract_question)  # type: ignore
graph.add_edge(START, "extract_question")
graph.add_edge("extract_question", END)

app = graph.compile()

if __name__ == "__main__":
    import asyncio
    import json
    from ai_workspace.utils import save_graph_visualization, to_serializable
    from backend_api.core.logging import logger

    async def main():
        save_graph_visualization(
            app,  # type: ignore
            filename="Question Extraction Image.png",
            base_path=r"ai_workspace/agents/code_generators/v5/graphs",
        )  # type: ignore

        image_paths = [r"images\mass_block.png"]

        results = []
        async for chunk in app.astream({"image_paths": image_paths}, stream_mode="values"):  # type: ignore
            print(chunk)
            results.append(chunk)

        # Save results to JSON
        with open(
            r"ai_workspace\agents\code_generators\v5\outputs\extract_question_image_output.json",
            "w",
        ) as f:
            json.dump(to_serializable(results), f, indent=3)
            logger.debug("Saved Output")

    asyncio.run(main())
