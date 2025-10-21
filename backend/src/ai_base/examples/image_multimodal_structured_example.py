"""
Example: Multimodal Image-to-LLM Interaction (Structured Output)

This example demonstrates how to send an image (in Base64 format) along with
a text prompt to a LangChain chat model initialized from project settings.
It also shows how to request a structured (Pydantic-validated) response.

Requires:
- `src.ai_base.settings.get_settings` for model configuration
- `src.ai_base.multimodel_io.image_multimodal` for multimodal payload creation
- `src.utils.to_serializable` for JSON-safe serialization of Pydantic models
"""

from pathlib import Path
from typing import List
from pydantic import BaseModel
from langchain.chat_models import init_chat_model
from src.ai_base.settings import get_settings
from src.ai_base.multimodel_io import image_multimodal
from src.utils import to_serializable
import json


class StructuredResponse(BaseModel):
    """Structured output schema returned by the model."""

    title: str
    key_concepts: List[str]


if __name__ == "__main__":
    # ---------------------------------------------------------------------
    # Model setup
    # ---------------------------------------------------------------------
    settings = get_settings()
    model_name = settings.base_model.model
    model_provider = settings.base_model.provider

    llm = init_chat_model(model=model_name, model_provider=model_provider)

    # ---------------------------------------------------------------------
    # Example image input
    # ---------------------------------------------------------------------
    test_image = Path("src/ai_base/examples/images/mass_block.png").resolve()

    # ---------------------------------------------------------------------
    # Structured multimodal example
    # ---------------------------------------------------------------------
    structured_prompt = "Extract a title and key concepts from the image."

    structured_response = image_multimodal(
        structured_prompt,
        llm=llm,
        image_paths=[test_image],
        output_model=StructuredResponse,
    )

    print("=== Structured Response ===")
    print(structured_response)

    # ---------------------------------------------------------------------
    # Save structured response to file
    # ---------------------------------------------------------------------
    structured_output_path = Path(
        "src/ai_base/examples/outputs/multimodal_structured_output.json"
    )
    structured_output_path.parent.mkdir(parents=True, exist_ok=True)
    structured_output_path.write_text(
        json.dumps(to_serializable(structured_response), indent=2),
        encoding="utf-8",
    )

    print(f"\nSaved structured response to {structured_output_path}\n")
