from langchain_core.prompts import ChatPromptTemplate


def extract_langsmith_prompt(base) -> str:
    try:
        if not isinstance(base, ChatPromptTemplate):
            raise ValueError("expected a ChatPromptTemplate")

        if not base.messages:
            raise ValueError("ChatPromptTemplate.messages is empty")

        messages = base.messages[0]
        if hasattr(messages, "prompt") and getattr(messages, "prompt") is not None and hasattr(messages.prompt, "template"):  # type: ignore
            template = messages.prompt.template  # type: ignore
        else:
            raise ValueError(f"Unsupported message type: {type(messages).__name__}")

        return template

    except Exception as e:
        raise ValueError(f"Could not extract prompt {str(e)}")
