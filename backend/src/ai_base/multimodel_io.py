from src.data_encoders import ImageEncoder
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
    encoded_images = encoder.prepare_llm_payload(image_paths,)
    message = {
        "role": "user",
        "content": [{"type": "text", "text": content}, *encoded_images],
    }
    
    if output_model:
        chain = llm.with_structured_output(schema=output_model)
        return chain.invoke([message])
    else:
        return llm.invoke([message])

