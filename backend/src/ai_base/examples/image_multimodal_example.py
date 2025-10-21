"""
Example: Multimodal Image-to-LLM Interaction

This example demonstrates how to send an image (in Base64 format) along with
a text prompt to a LangChain chat model initialized from project settings.
It also shows how to request a structured (Pydantic-validated) response.

Requires:
- `src.ai_base.settings.get_settings` for model configuration
- `src.ai_base.multimodel_io.image_multimodal` for multimodal payload creation
- `src.utils.to_serializable` for JSON-safe serialization of model outputs
"""

from pathlib import Path
from typing import List
from pydantic import BaseModel
from langchain.chat_models import init_chat_model
from src.ai_base.settings import get_settings
from src.ai_base.multimodel_io import image_multimodal
from src.utils import to_serializable
import json


if __name__ == "__main__":
    # ---------------------------------------------------------------------
    # Model setup
    # ---------------------------------------------------------------------
    settings = get_settings()
    model_name = settings.base_model.model
    model_provider = settings.base_model.provider

    llm = init_chat_model(model=model_name, model_provider=model_provider)

    # ---------------------------------------------------------------------
    # Basic multimodal example
    # ---------------------------------------------------------------------
    test_image = Path("src/ai_base/examples/images/mass_block.png").resolve()
    base_prompt = "What is in the image?"

    response = image_multimodal(base_prompt, llm=llm, image_paths=[test_image])

    print("=== Raw Response ===")
    print(response)

    # ---------------------------------------------------------------------
    # Save the raw response to a file
    # ---------------------------------------------------------------------
    output_path = Path("src/ai_base/examples/outputs/multimodal_raw_output.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(to_serializable(response), indent=2),
        encoding="utf-8",
    )

    print(f"\nSaved raw response to {output_path}\n")
