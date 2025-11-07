import {
    TagAttributeMapping,
    type TagRegistry,
    type ValidComponents,
    ComponentMap,
} from "./questionComponentMapping";
import parse, { domToReact } from "html-react-parser";
import type { DOMNode } from "html-react-parser";
import { MathJax } from "better-react-mathjax";
import { useState } from "react";

const isValidTagName = (val: string): val is keyof TagRegistry => {
    return val in TagAttributeMapping;
};
// Shorthand essentially get value of the Valid components and use it
// as a mapping
type TransformTagType<K extends ValidComponents> = {
    tagName: K;
    Tag: (typeof ComponentMap)[K];
    transformedProps: TagRegistry[K];
};

function TransformTag<K extends ValidComponents>(
    node: DOMNode
): TransformTagType<K> | undefined {
    if (node.type === "tag") {
        const tagName = node.name.toLowerCase();

        if (isValidTagName(tagName)) {
            const Tag = ComponentMap[tagName];

            console.log("Got node as tag", node)
            const transform = TagAttributeMapping[tagName];
            const transformedProps = transform(node.attribs);

            return {
                tagName,
                Tag,
                transformedProps,
            } as TransformTagType<K>;
        }
    }
}

export const HandleTags = (node: DOMNode) => {
    try {
        if (node.type !== "tag") return null;

        const result = TransformTag(node);
        if (!result) return null;

        const { Tag, transformedProps } = result;
        if (!Tag) return null;

        let children: React.ReactNode = null;

        if (node.childNodes?.length) {
            try {
                children = domToReact(node.children as DOMNode[], {
                    replace: (child: any) => {
                        try {
                            if (child.type === "tag") {
                                const childResult = TransformTag(child);
                                if (!childResult) return null;

                                const { Tag: ChildTag, transformedProps: ChildAttrs } = childResult;
                                if (!ChildTag) return null;

                                return (
                                    <ChildTag {...ChildAttrs}>
                                        {domToReact(child.children)}
                                    </ChildTag>
                                );
                            }
                        } catch (err) {
                            console.error("Error transforming child tag:", err, child);
                            return null;
                        }
                    },
                });
            } catch (err) {
                console.error("Error parsing child nodes:", err, node);
            }
        }

        return <Tag {...transformedProps}>{children}</Tag>;
    } catch (err) {
        console.error("Error handling tag:", err, node);
        return (
            <span style={{ color: "red", fontStyle: "italic" }}>
                [Render error: invalid tag]
            </span>
        );
    }
};


export function QuestionHTMLToReact({ html }: { html: string }) {
    let parsed;
    try {
        parsed = parse(html, { replace: (node) => HandleTags(node) })
    } catch (error) {
        console.log(error)
        parsed = html
    }

    return <> <MathJax>{parsed}</MathJax></>
}