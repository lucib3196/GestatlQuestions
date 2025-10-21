
---

### `messages_example.py`

**Purpose:**
Demonstrates the basics of how to pass messages to an AI BaseModel using LangChain’s chat interface.

**Description:**
This example shows how to initialize and interact with a chat model through the `init_chat_model` function.
It highlights two input methods:

1. **Structured Message Objects** — Uses `SystemMessage` and `HumanMessage` to exchange messages.
2. **Dictionary-Based Input** — Sends messages as role-based dictionaries for flexible control.

Serves as a minimal reference for verifying model connectivity and understanding message flow.

---

### `tool_call_example.py`

**Purpose:**
Demonstrates how to bind and use external Python functions (“tools”) with a LangChain chat model.

**Description:**
Initializes a chat model using environment-based configuration, then binds a custom function (`get_weather`) as a callable tool.
The model recognizes when to call the tool and executes it dynamically—showing how to integrate external logic or APIs into the model workflow.

---

### `image_multimodal_example.py`

**Purpose:**
Showcases how to send an image with a text prompt to a multimodal chat model and receive a standard text response.

**Description:**
Encodes an image to Base64 and passes it, along with a text prompt, through the `image_multimodal` function.
Useful for validating multimodal input handling and visual reasoning capabilities of the model.

---

### `image_multimodal_structured_example.py`

**Purpose:**
Demonstrates multimodal image input with structured (Pydantic-validated) output.

**Description:**
Uses the same image-to-model workflow but requests a structured response conforming to a `BaseModel` schema (e.g., `title`, `key_concepts`).
Highlights how to extract organized information from visual prompts.

---

### `pdf_multimodal_example.py`

**Purpose:**
Illustrates how to send a PDF document to a multimodal chat model for open-ended analysis or summarization.

**Description:**
Converts or uploads a PDF and sends it to the LLM alongside a text query using `pdf_multimodal`.
The model produces a natural-language description or summary of the document’s contents.

---

### `pdf_multimodal_structured_example.py`

**Purpose:**
Demonstrates structured output generation from PDF-based multimodal input.

**Description:**
Similar to the basic PDF example but returns a structured response validated by a Pydantic schema (e.g., `title`, `key_concepts`).
Ideal for extracting key information from academic or technical documents.

---


## Notes

- The PDF multimodal function converts all pages into images and sends them as a single payload. While this works, it can be inefficient for rich content extraction since it 
consumes more tokens. The function currently processes one PDF at a time, though it could be extended to handle multiple PDFs — 
in most cases, however, processing a single document per call is preferred.
