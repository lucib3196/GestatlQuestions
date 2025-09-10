import asyncio
import base64

from typing import List, Union, Type, Optional

from pydantic import BaseModel, Field

from src.api.core.logging import logger

from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.messages import HumanMessage

from langchain_openai import ChatOpenAI


async def encode_image(image_path: str):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    except Exception as e:
        logger.info(f"Error Encoding Image {image_path}: {e}")
        raise


async def encode_multiple_images(image_paths: List[str]) -> List[str]:
    try:
        return await asyncio.gather(
            *(encode_image(image_path) for image_path in image_paths)
        )
    except Exception as e:
        logger.info(f"Error Encoding Multiple Images Error: {e}")
        raise


async def create_image_content_payload(image_paths: List[str]) -> List[dict]:
    encoded_images = await encode_multiple_images(image_paths)
    image_contents = [
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image}", "detail": "high"},
        }
        for image in encoded_images
    ]
    return image_contents


class ImageLLMProcessor:
    def __init__(
        self,
        prompt: Union[str, ChatPromptTemplate],
        schema: Optional[Type[BaseModel]],
        model="gpt-4o",
        include_raw: bool = False,
    ):
        self.llm = ChatOpenAI(model=model)
        if schema:
            self.llm = self.llm.with_structured_output(
                schema=schema, include_raw=include_raw
            )
        self.processed_prompt = (
            prompt.messages[0].prompt.template  # type: ignore
            if isinstance(prompt, ChatPromptTemplate)  # type: ignore
            else prompt
        )
        if not self.processed_prompt:
            logger.error("Error loading in the prompt")
            raise ValueError("Could not process prompt")

    async def prepare_paload(self, image_paths: List[str]):
        if not image_paths:
            raise ValueError("Image Paths cannot be empty")
        try:
            image_contents = await create_image_content_payload(image_paths)
            message = HumanMessage(
                content=[
                    {"type": "text", "text": self.processed_prompt},  # type: ignore
                    *image_contents,
                ],
            )
            return message
        except Exception as e:
            logger.error(f"Error Occured Preparing the image payload {e}")

    async def send_arequest(self, image_paths: List[str]):
        try:
            message = await self.prepare_paload(image_paths)
            response = await self.llm.ainvoke([message])  # type: ignore
            return response
        except Exception as e:
            logger.error(f"Error sending image request {e}")


if __name__ == "__main__":
    from ai_workspace.models.payloads import Question
    from ai_workspace.utils import to_serializable
    import json
    from langchain import hub

    class Response(BaseModel):
        description: List[Question]

    prompt = hub.pull("extract-all-questions")
    image_paths = [r"images\mass_block.png"]
    extractor = ImageLLMProcessor(prompt=prompt, schema=Response, model="gpt-5-mini")
    results = asyncio.run(extractor.send_arequest(image_paths))
    with open(r"ai_workspace\image_processing\test.json", "w") as f:
        json.dump(to_serializable(results), f)
