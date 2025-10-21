### `messages_example.py`

**Purpose:**  
Demonstrates the basics of how to pass messages to an AI BaseModel using LangChain’s chat interface.

**Description:**  
This example shows how to initialize and interact with a chat model through the `init_chat_model` function.  
Model configuration details (such as provider, model name, and API key) are automatically loaded from the project’s environment using `get_settings()`.

Two interaction methods are illustrated:
1. **Structured Message Objects** — Uses `SystemMessage` and `HumanMessage` to send a conversation and receive an `AIMessage` response.
2. **Dictionary-Based Input** — Sends messages as dictionaries with explicit roles (`system`, `user`, `assistant`) for flexible input handling.

This script serves as a minimal reference for verifying model connectivity, configuration loading, and understanding message flow in multimodal or chat-based applications.
