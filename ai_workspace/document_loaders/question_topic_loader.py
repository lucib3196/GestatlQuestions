import json
from typing import AsyncIterator, Iterator
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from ai_workspace.models import FullTopicDescriptionList
import aiofiles  # type: ignore


class TopicDocumentLoader(BaseLoader):
    def __init__(self, filepath: str) -> None:
        self.file_path = filepath

    def lazy_load(self) -> Iterator[Document]:
        with open(self.file_path, encoding="utf-8") as f:
            full = FullTopicDescriptionList(**json.load(f))
            for topic in full.topics:
                yield Document(
                    page_content=f"Topic Name: {topic.name}\n Engineering Disciplines: {", ".join(topic.discipline)}\n Description: {topic.description}",
                    metadata={
                        "source": "topic list",
                        "topic_name": {topic.name},
                        "topic_description": {topic.description},
                    },
                )

    async def alazy_load(self) -> AsyncIterator[Document]:
        async with aiofiles.open(self.file_path, encoding="utf-8") as f:
            full = FullTopicDescriptionList(**json.load(f))  # type: ignore
            for topic in full.topics:
                yield Document(
                    page_content=f"Topic Name: {topic.name}\n Engineering Disciplines {topic.discipline}\n Description: {topic.description}",
                    metadata={
                        "source": "topic list",
                        "topic_name": {topic.name},
                        "topic_description": {topic.description},
                    },
                )


if __name__ == "__main__":
    filepath = r"./data/topic_data_description.json"
    loader = TopicDocumentLoader(filepath=filepath)
    print("Testing Document Loader")
    for doc in loader.lazy_load():
        print()
        print(type(doc))
        print(doc)
