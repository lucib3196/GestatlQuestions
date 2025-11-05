import {
    TagAttributeMapping,
    type TagRegistry,
    type ValidComponents,
    ComponentMap,
} from "./questionComponentMapping";
import parse, { domToReact } from "html-react-parser";
import type { DOMNode } from "html-react-parser";
import { MathJax } from "better-react-mathjax";

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

const HandleTags = (node: DOMNode) => {
    if (node.type === "tag") {
        const result = TransformTag(node);

        if (result) {
            const { Tag, transformedProps } = result;

            if (!Tag) return null;

            const children = node.childNodes?.length
                ? domToReact(node.children as DOMNode[], {
                    replace: (child: any) => {
                        if (child.type === "tag") {
                            const childResult = TransformTag(child);

                            if (childResult) {
                                const { Tag: ChildTag, transformedProps: ChildAttrs } =
                                    childResult;
                                if (!ChildTag) return null;
                                return (
                                    <ChildTag {...ChildAttrs}>
                                        {domToReact(child.children)}
                                    </ChildTag>
                                );
                            }
                        }
                    },
                })
                : null;

            return <Tag {...transformedProps}>{children}</Tag>;
        }
    }
};


export function QuestionHTMLToReact({ html }: { html: string }) {
    const parsedFile = parse(html, { replace: (node) => HandleTags(node) })

    return <> <MathJax>{parsedFile}</MathJax></>
}