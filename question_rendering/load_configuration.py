from __future__ import annotations
import json
from typing import List
from .models import TagConfig
from bs4 import BeautifulSoup
from typing import Generator, Iterable
from .tag_replacer import TagReplacer

# TagConfigs: List[TagConfig]


def load():
    with open("question_rendering/tag_config.json", "r") as f:
        data = json.load(f)
    return [TagConfig(**cfg) for cfg in data]


def apply_all_replacers(
    html: str | BeautifulSoup,
    tag_configs: Iterable[TagConfig] | None = None,
):
    soup = (
        html if isinstance(html, BeautifulSoup) else BeautifulSoup(html, "html.parser")
    )
    print(soup)
    tag_configs = tag_configs or load()
    for idx, cfg in enumerate(tag_configs, 1):
        print("Current Soup\n", soup)
        soup = TagReplacer(
            soup,
            cfg,
        ).transform()  # type: ignore
        print("New Soup\n", soup)
    return soup


if __name__ == "__main__":
    ## Things to add I need to add all the other tags including dealing with other content inside the tag and simplify the
    ## Logic when possible
    html = "<pl_question_panel>Some Content</pl_question_panel><pl_symbolic_input>Some Content</pl_symbolic_input>"

    print(apply_all_replacers(html=html))
