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


### `tool_call_example.py`
**Purpose:**  
Demonstrates how to bind and use external Python functions ("tools") with a LangChain chat model.

**Description:**  
This example initializes a chat model using environment-based configuration and then binds a custom Python function (`get_weather`) as a callable tool.  
The model is prompted with a weather-related query, automatically detects the need for the tool, and invokes it with the appropriate arguments.  

This example shows how to integrate external logic or APIs with a chat model—allowing it to execute real-world functions and return results.