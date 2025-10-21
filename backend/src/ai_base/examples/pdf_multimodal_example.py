"""
Example: PDF-to-LLM Multimodal Interaction (Basic Output)

This example demonstrates how to send a PDF file to a LangChain chat model
initialized from project settings. The model analyzes the document and
returns a standard text-based response.

Requires:
- `src.ai_base.settings.get_settings` for model configuration
- `src.ai_base.multimodel_io.pdf_multimodal` for PDF processing
"""

from pathlib import Path
from langchain.chat_models import init_chat_model
from src.ai_base.settings import get_settings
from src.ai_base.multimodel_io import pdf_multimodal
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
    pdf_path = Path("src/ai_base/examples/images/HeatProblems.pdf").resolve()
    prompt = "What is in the document?"

    response = pdf_multimodal(content=prompt, llm=llm, pdf_path=pdf_path)

    print("=== Raw Response ===")
    print(response)

    # ---------------------------------------------------------------------
    # Save output to file
    # ---------------------------------------------------------------------
    output_path = Path("src/ai_base/examples/outputs/pdf_multimodal_raw_output.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(to_serializable(response), indent=2),
        encoding="utf-8",
    )

    print(f"\nSaved raw response to {output_path}\n")
