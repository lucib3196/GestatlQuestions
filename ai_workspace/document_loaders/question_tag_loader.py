import os
import numpy as np
from typing import Iterator
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
import json
from typing import AsyncIterator, Iterator
from ai_workspace.models import AllQuestionTagDescription
import aiofiles  # type: ignore


class QuestionTagLoader(BaseLoader):
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def lazy_load(self) -> Iterator[Document]:
        with open(self.file_path, encoding="utf-8") as f:
            full = AllQuestionTagDescription(**json.load(f))
            for tag in full.descriptions:
                attributes = "\n".join(
                    f"- **{att.name}**: {att.description}" for att in tag.attrs
                )
                page_content = (
                    f"## <{tag.name}> Tag\n\n"
                    f"**Description:** {tag.description}\n\n"
                    f"**Example:**\n"
                    f"```html\n{tag.sample}\n```\n\n"
                    f"**Attributes:**\n"
                    f"{attributes if attributes else 'None'}"
                )
                yield Document(
                    page_content=page_content,
                    metadata={
                        "source": "tag list",
                        "tag_name": tag.name,
                        "type": tag.type,
                    },
                )

    async def alazy_load(self) -> AsyncIterator[Document]:
        async with aiofiles.open(self.file_path, encoding="utf-8") as f:
            content = await f.read()
            full = AllQuestionTagDescription(**json.loads(content))
            for tag in full.descriptions:
                attributes = "\n".join(
                    f"- **{att.name}**: {att.description}" for att in tag.attrs
                )
                page_content = (
                    f"## <{tag.name}> Tag\n\n"
                    f"**Description:** {tag.description}\n\n"
                    f"**Example:**\n"
                    f"```html\n{tag.sample}\n```\n\n"
                    f"**Attributes:**\n"
                    f"{attributes if attributes else 'None'}"
                )
                yield Document(
                    page_content=page_content, metadata={"source": "tag list"}
                )


if __name__ == "__main__":
    filepath = r"data/question_element_tags.json"
    loader = QuestionTagLoader(file_path=filepath)
    print("Testing Document Loader")
    for doc in loader.lazy_load():
        print()
        print(type(doc))
        print(doc)
