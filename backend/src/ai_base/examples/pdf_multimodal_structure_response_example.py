"""
Example: PDF-to-LLM Multimodal Interaction (Structured Output)

This example demonstrates how to send a PDF file to a LangChain chat model
and request a structured (Pydantic-validated) response.

Requires:
- `src.ai_base.settings.get_settings` for model configuration
- `src.ai_base.multimodel_io.pdf_multimodal` for PDF processing
- `src.utils.to_serializable` for JSON-safe serialization
"""

from pathlib import Path
from typing import List
from pydantic import BaseModel
from langchain.chat_models import init_chat_model
from src.ai_base.settings import get_settings
from src.ai_base.multimodel_io import pdf_multimodal
from src.utils import to_serializable
import json


class StructuredResponse(BaseModel):
    """Structured schema returned by the model."""
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
    # Structured multimodal example
    # ---------------------------------------------------------------------
    pdf_path = Path("src/ai_base/examples/images/HeatProblems.pdf").resolve()
    prompt = "Extract a title and key concepts from the document."

    response = pdf_multimodal(
        content=prompt,
        llm=llm,
        pdf_path=pdf_path,
        output_model=StructuredResponse,
    )

    print("=== Structured Response ===")
    print(response)

    # ---------------------------------------------------------------------
    # Save structured output to file
    # ---------------------------------------------------------------------
    output_path = Path(
        "src/ai_base/examples/outputs/pdf_multimodal_structured_output.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(to_serializable(response), indent=2),
        encoding="utf-8",
    )

    print(f"\nSaved structured response to {output_path}\n")
