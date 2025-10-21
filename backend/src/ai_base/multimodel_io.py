from src.data_encoders import ImageEncoder, pdf_page_to_image_bytes
from typing import List, Type, Optional
from pydantic import BaseModel
from .base_models import BaseOutput
from pathlib import Path
from langchain_core.language_models.chat_models import BaseChatModel
import fitz


def image_multimodal(
    content: str,
    llm: BaseChatModel,
    image_paths: List[str | Path],
    output_model: Optional[Type[BaseModel]] = BaseOutput,
):
    encoder = ImageEncoder()
    encoded_images = encoder.prepare_llm_payload(
        image_paths,
    )
    message = {
        "role": "user",
        "content": [{"type": "text", "text": content}, *encoded_images],
    }

    if output_model:
        chain = llm.with_structured_output(schema=output_model)
        return chain.invoke([message])
    else:
        return llm.invoke([message])


def pdf_multimodal(
    content: str,
    llm: BaseChatModel,
    pdf_path: str | Path,
    output_model: Optional[Type[BaseModel]] = BaseOutput,
):
    pdf_bytes = pdf_page_to_image_bytes(pdf_path)
    encoder = ImageEncoder()
    encoded_images = encoder.prepare_llm_payload(
        pdf_bytes,
    )
    message = {
        "role": "user",
        "content": [{"type": "text", "text": content}, *encoded_images],
    }

    if output_model:
        chain = llm.with_structured_output(schema=output_model)
        return chain.invoke([message])
    else:
        return llm.invoke([message])


if __name__ == "__main__":
    # The code snippet you provided is setting up a language model for a chat application and then
    # using it to process a PDF document. Here's a breakdown of what each part of the code is doing:
    from src.ai_base.settings import get_settings
    from langchain.chat_models import init_chat_model

    settings = get_settings()
    model_name = settings.base_model.model
    model_provider = settings.base_model.provider

    llm = init_chat_model(model=model_name, model_provider=model_provider)
    pdf_path = Path(r"src\ai_base\examples\images\HeatProblems.pdf").resolve()
    response = pdf_multimodal(content="What is in the document", llm=llm, pdf_path=pdf_path,)
    