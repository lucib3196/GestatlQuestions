from src.data_parser import ImageEncoder, pdf_page_to_image_bytes
from typing import List, Type, Optional
from pydantic import BaseModel
from .base_models import BaseOutput
from pathlib import Path
from langchain_core.language_models.chat_models import BaseChatModel


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


class PDFMultiModal:
    def prepare_payload(self, pdf_path: str | Path, prompt: str):
        pdf_bytes = pdf_page_to_image_bytes(pdf_path)
        encoder = ImageEncoder()
        encoded_images = encoder.prepare_llm_payload(pdf_bytes)
        message = {
            "role": "user",
            "content": [{"type": "text", "text": prompt}, *encoded_images],
        }
        return message

    def invoke(
        self,
        prompt: str,
        llm: BaseChatModel,
        pdf_path: str | Path,
        output_model: Optional[Type[BaseModel]] = BaseOutput,
    ):
        message = self.prepare_payload(pdf_path, prompt)
        if output_model:
            chain = llm.with_structured_output(schema=output_model)
            return chain.invoke([message])
        else:
            return llm.invoke([message])

    def ainvoke(
        self,
        prompt: str,
        llm: BaseChatModel,
        pdf_path: str | Path,
        output_model: Optional[Type[BaseModel]] = BaseOutput,
    ):
        message = self.prepare_payload(pdf_path, prompt)
        if output_model:
            chain = llm.with_structured_output(schema=output_model)
            return chain.ainvoke([message])
        else:
            return llm.ainvoke([message])
