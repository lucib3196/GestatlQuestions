from .models import TagConfig, Config
from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString
from typing import List, Mapping, Any, Union, Optional
import json
from copy import copy


class TagReplacer:
    def __init__(
        self,
        html: str | BeautifulSoup,
        tag_configuration: TagConfig,
        config: Config = Config(
            separate_forms_per_input=True
        ),  # Model has default values
    ):
        self.soup: BeautifulSoup = (
            html
            if isinstance(html, BeautifulSoup)
            else BeautifulSoup(html, "html.parser")
        )
        self.tag_config = tag_configuration
        self.config = config

    def transform(self) -> Optional[BeautifulSoup]:
        target_tags = list(self.soup.find_all(self.tag_config.target_tag))
        if not target_tags:
            return self.soup

        for tag in target_tags:
            if not isinstance(tag, Tag):
                continue  # Skip invalid tags
            # Check the type of tag that we ar dealing witn wether input, decorative or other

            render_type = self.tag_config.render_role
            if render_type == "decorative":
                return self._handle_decorative_elements(tag)
            elif render_type == "input":
                return self._handle_input_elements(tag)
            else:
                raise NotImplementedError("Have not implemented other type")

    def _handle_decorative_elements(self, tag):
        old_attrs = tag.attrs
        # Find matching config for div and p more to be added as needed
        div_config = next((m for m in self.tag_config.mapping if m.name == "div"), None)
        p_config = next((m for m in self.tag_config.mapping if m.name == "p"), None)

        # Create new <div> tag with attributes if config is present
        div_tag = self.soup.new_tag(
            "div", attrs=div_config.attributes if div_config else {}
        )
        self._map_attributes(old_attributes=old_attrs, new_attributes=div_tag.attrs)  # type: ignore

        # If p_config exists, create and append a <p> tag inside the div
        if p_config:
            p_tag = self.soup.new_tag("p", attrs=p_config.attributes)
            self._map_attributes(old_attributes=old_attrs, new_attributes=p_tag.attrs)  # type: ignore
            p_tag.string = tag.text
            div_tag.append(p_tag)
        else:
            for child in tag.children:
                div_tag.append(copy(child))

        tag.replace_with(div_tag)
        return self.soup

    def _handle_input_elements(self, tag):
        old_attrs = tag.attrs
        input_config = next(
            (m for m in self.tag_config.mapping if m.name == "input"), None
        )
        # Handle input type elements
        input_tag = self.soup.new_tag(
            "input", attrs=input_config.attributes if input_config else {}
        )
        self._map_attributes(
            old_attributes=old_attrs, new_attributes=input_tag.attrs  # type: ignore
        )
        if self.config.separate_forms_per_input and input_tag:
            # === Create label ===
            label_config = next(
                (m for m in self.tag_config.mapping if m.name == "label"), None
            )
            label_tag = self.soup.new_tag(
                "label", attrs=label_config.attributes if label_config else {}
            )
            label_tag.string = label_tag.attrs.get("text", "Answer")  # type: ignore

            # === Create legend ===
            legend_config = next(
                (m for m in self.tag_config.mapping if m.name == "legend"), None
            )
            legend_tag = self.soup.new_tag(
                "legend",
                attrs=legend_config.attributes if legend_config else {},
            )
            legend_tag.string = legend_tag.attrs.get("text", "Answer")  # type: ignore

            # === Create fieldset ===
            fieldset_config = next(
                (m for m in self.tag_config.mapping if m.name == "fieldset"),
                None,
            )
            fieldset_tag = self.soup.new_tag(
                "fieldset",
                attrs=fieldset_config.attributes if fieldset_config else {},
            )
            fieldset_tag.append(legend_tag)
            fieldset_tag.append(label_tag)
            fieldset_tag.append(input_tag)

            # === Create form ===
            form_config = next(
                (m for m in self.tag_config.mapping if m.name == "form"), None
            )
            form_tag = self.soup.new_tag(
                "form", attrs=form_config.attributes if form_config else {}
            )
            form_tag.append(fieldset_tag)

            # === Replace the original tag ===
            tag.replace_with(form_tag)
        else:
            tag.replace_with(input_tag)
        return self.soup

    def _map_attributes(
        self, old_attributes: Mapping[str, str], new_attributes: dict[str, str]
    ) -> dict[str, Any]:
        new_attrs = {
            new_key: old_attributes[old_key]
            for old_key, new_key in new_attributes.items()
            if old_key in old_attributes
        }
        unmapped_attrs = set(old_attributes) - set(new_attributes)
        if unmapped_attrs:
            print("Unmapped attributes encountered: %s", unmapped_attrs)
        return new_attrs


if __name__ == "__main__":

    with open(r"question_rendering/tag_config.json", "r") as f:
        data: List[TagConfig] = json.load(f)
        config: TagConfig = data[0]
        print(config)
    replacer = TagReplacer(
        html="<pl_question_panel><pl_symbolic_input>Some Content</pl_symbolic_input></pl_question_panel>",
        tag_configuration=TagConfig(**config),  # type: ignore
    )
    print(replacer.transform())
