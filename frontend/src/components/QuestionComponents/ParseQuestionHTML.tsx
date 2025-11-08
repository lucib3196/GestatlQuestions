import {
    TagAttributeMapping,
    type TagRegistry,
    type ValidComponents,
    ComponentMap,
} from "./questionComponentMapping";
import parse, { domToReact } from "html-react-parser";
import type { DOMNode } from "html-react-parser";
import { MathJax } from "better-react-mathjax";
import React from "react";

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

class SafeRenderer extends React.Component<
    { children: React.ReactNode },
    { hasError: boolean; errorMessage?: string }
> {
    constructor(props) {
        super(props);
        this.state = { hasError: false, errorMessage: "" }
    }

    static getDerivedStateFromError(error: unknown) {
        const message =
            error instanceof Error ? error.message : String(error);
        return { hasError: true, errorMessage: message };
    }

    componentDidCatch(error: any, info: any) {
        console.error("Render failed:", error, info);
    }

    render() {
        if (this.state.hasError) {
            return <div>⚠️ Failed to render content {this.state.errorMessage} </div>;
        }
        return this.props.children;
    }
}

function getChildrenSafe(node: unknown): React.ReactNode | null {
    if (!React.isValidElement(node)) return null;

    const props = (node as Record<string, any>).props;

    if (!Object.prototype.hasOwnProperty.call(props, "children")) {
        return null;
    }
    return props.children ?? null;
}

export function CleanNode(node: unknown) {
    if (typeof node === "string") {
        const trimmed = node.replace(/\r?\n|\r/g, "").trim();
        return trimmed.length > 0 ? (
            <React.Fragment>{trimmed}</React.Fragment>
        ) : null;
    }
    if (React.isValidElement(node)) {
        const children = getChildrenSafe(node);

        if (children) {
            // Recursivley clean
            const cleanedChildren = Array.isArray(children)
                ? children.map((child, i) => {
                    console.log("Cleaning Child", child);
                    return <React.Fragment key={i}>{CleanNode(child)}</React.Fragment>;
                })
                : null;
            return React.cloneElement(node, {
                ...node.props,
                children: cleanedChildren,
            });
        }

        console.log("Node passed cleaning this is the node", node);

        // no Children
        return node;
    }

    console.warn("Skipped invalid React child:", node);
    return null;
}

function TransformTag<K extends ValidComponents>(
    node: DOMNode
): TransformTagType<K> | undefined {
    try {
        if (node.type === "tag") {
            const tagName = node.name.toLowerCase();

            if (isValidTagName(tagName)) {
                const Tag = ComponentMap[tagName];
                const transform = TagAttributeMapping[tagName];
                const transformedProps = transform(node.attribs);

                return {
                    tagName,
                    Tag,
                    transformedProps,
                } as TransformTagType<K>;
            }
        }
    } catch (error) {
        console.log("Error transforming tag", error);
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

                                const { Tag: ChildTag, transformedProps: ChildAttrs } =
                                    childResult;
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
        parsed = parse(html, { replace: (node) => HandleTags(node) });
    } catch (error) {
        console.log(error);
        parsed = html;
    }
    

    return (
        <SafeRenderer>
            <MathJax>{parsed}</MathJax>
        </SafeRenderer>
    );
}
