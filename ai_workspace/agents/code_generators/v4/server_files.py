from typing import Optional, Literal
from textwrap import dedent
from langchain import hub
from langchain_community.vectorstores import FAISS
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langgraph.graph import END, START, StateGraph
from langsmith import Client
from pydantic import BaseModel

from ai_workspace.models import CodeResponse
from ai_workspace.retrievers import SemanticExamplesCSV
from ai_workspace.utils import parse_structured, save_graph_visualization


client = Client()
# ────────────────────────────────────────────────────────────────────────────────
# Constants
# ────────────────────────────────────────────────────────────────────────────────
FASTLLM = "gpt-4o-mini"
LONGCONTEXTLLM = "o3-mini-2025-01-31"
QUESTION_VECTOR_STORE_PATH = r"ai_workspace\vectorstores\QUESTIONMOD_VS"
N_SEARCH_QUERIES = 3
CSV_PATH = r"data\QuestionDataV2_06122025_classified.csv"

# Initialize LLMs
fast_llm = ChatOpenAI(model=FASTLLM)
long_context_llm = ChatOpenAI(model=LONGCONTEXTLLM)

# ────────────────────────────────────────────────────────────────────────────────
# Vector store & retriever
# ────────────────────────────────────────────────────────────────────────────────
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

q_vectorstore = FAISS.load_local(
    QUESTION_VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True
)

# Question retriever and formatter
q_retriever_js = SemanticExamplesCSV(
    column_names=["question.html", "server.js"],
    csv_path=CSV_PATH,
    vector_store=q_vectorstore,
)
q_retriever_py = SemanticExamplesCSV(
    column_names=["question.html", "server.py"],
    csv_path=CSV_PATH,
    vector_store=q_vectorstore,
)


# ────────────────────────────────────────────────────────────────────────────────
# State and Function Definitions
# ────────────────────────────────────────────────────────────────────────────────
class State(BaseModel):
    original_question: str
    question_html: str
    solution_guide: Optional[str] = None
    isAdaptive: bool = True
    server_file: str = ""
    test_parameters: Optional[str] = None


def generate_server_js(state: State):
    """
    Generate server.js based on the provided question and (optional) solution guide.
    """
    base_prompt = client.pull_prompt("server_js_template_base")

    # Apply retriever filter and build the prompt
    q_retriever_js.set_filter({"isAdaptive": state.isAdaptive})
    prompt = q_retriever_js.format_template(
        query=state.question_html, k=1, base_template=base_prompt
    )
    messages = prompt.format_messages(question=state.question_html)  # type: ignore

    # Inject the solution guide exactly once (as a SystemMessage), if provided
    if state.solution_guide:
        solution_prompt = dedent(
            f"""
            You are provided with the following solution guide. Use its reasoning, steps,
            and methodology as the primary reference for the JavaScript (server.js) implementation.
            Expand steps where necessary for clarity, but ensure the structure and logic of the
            JavaScript output closely follow the guide's approach.

            Solution Guide:
            {state.solution_guide}
        """
        ).strip()

        last_sys_idx = max(
            (i for i, m in enumerate(messages) if isinstance(m, SystemMessage)),
            default=-1,
        )
        insert_idx = last_sys_idx + 1
        messages = (
            messages[:insert_idx]
            + [SystemMessage(content=solution_prompt)]
            + messages[insert_idx:]
        )

    # Generate the server.js code
    chain = fast_llm.with_structured_output(CodeResponse, include_raw=True)
    result = chain.invoke(messages)
    ai_message = result["raw"]
    structured = parse_structured(CodeResponse, ai_message)
    return {"server_file": structured.code}


def generate_server_py(state: State):
    """
    Generate server.py based on the provided question and solution guide.
    """
    base_prompt = client.pull_prompt("server_py_template_base1")

    q_retriever_py.set_filter({"isAdaptive": state.isAdaptive})
    prompt = q_retriever_py.format_template(
        query=state.question_html, k=1, base_template=base_prompt
    )
    messages = prompt.format_messages(question=state.question_html)  # type: ignore

    # Add solution guide to the messages if provided
    last_sys_idx = max(
        (i for i, m in enumerate(messages) if isinstance(m, SystemMessage)), default=-1
    )
    if state.solution_guide:
        solution_prompt = f"""
            "\n\nAdditionally, you are provided with the following solution guide. "
            "This solution guide outlines the intended approach and logic for solving the question. "
            "You must use the reasoning, steps, and methodology from this guide as the primary reference for how the question should be implemented and transformed into the Python (server.py) file. "
            "Expand on the steps where necessary for clarity, but ensure that the structure and logic of the Python output closely follow the solution guide's approach."
            f"\n\nSolution Guide:\n{state.solution_guide.replace('{', '{{').replace('}', '}}')}\n"""
        solution_msg = SystemMessage(content=solution_prompt)
        insert_idx = last_sys_idx + 1
        messages = messages[:insert_idx] + [solution_msg] + messages[insert_idx:]

    # Generate the server.py code
    chain = fast_llm.with_structured_output(CodeResponse, include_raw=True)
    result = chain.invoke(messages)
    ai_message = result["raw"]
    structured = parse_structured(CodeResponse, ai_message)
    return {"server_file": structured.code}


def router(state: State):  # type: ignore
    if state.test_parameters:
        return "generate_test"
    else:
        return END


def generate_test_js(state: State):
    base_prompt = client.pull_prompt("server_test")
    chain = base_prompt | fast_llm.with_structured_output(
        CodeResponse, include_raw=True
    )
    result = chain.invoke(
        {
            "original_question": state.original_question,
            "question": state.server_file,
            "parameters": state.test_parameters,
        }
    )
    ai_message = result["raw"]
    structured = parse_structured(CodeResponse, ai_message)
    return {"server_file": structured.code}


def generate_test_py(state: State):
    base_prompt = client.pull_prompt("server_test_py")
    chain = base_prompt | fast_llm.with_structured_output(
        CodeResponse, include_raw=True
    )
    result = chain.invoke(
        {
            "original_question": state.original_question,
            "question": state.server_file,
            "parameters": state.test_parameters,
        }
    )
    ai_message = result["raw"]
    structured = parse_structured(CodeResponse, ai_message)
    return {"server_file": structured.code}


# ────────────────────────────────────────────────────────────────────────────────
# Workflow Setup
# ────────────────────────────────────────────────────────────────────────────────
# Workflow for server.js generation
workflow = StateGraph(State)
workflow.add_node("generate_server_js", generate_server_js)
workflow.add_node("generate_test", generate_test_js)

workflow.add_edge(START, "generate_server_js")

workflow.add_conditional_edges("generate_server_js", router, [END, "generate_test"])

workflow.add_edge("generate_test", END)
app = workflow.compile()

# Workflow for server.py generation
workflow_py = StateGraph(State)
workflow_py.add_node("generate_server_py", generate_server_py)
workflow_py.add_node("generate_test", generate_test_py)

workflow_py.add_edge(START, "generate_server_py")
workflow_py.add_conditional_edges("generate_server_py", router, [END, "generate_test"])

workflow_py.add_edge("generate_test", END)
app_py = workflow_py.compile()

# ────────────────────────────────────────────────────────────────────────────────
# Main Execution
# ────────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    save_graph_visualization(
        app,  # type: ignore
        "serverjs_graph.png",
        base_path=r"ai_workspace\agents\code_generators\v4\graphs",
    )
    save_graph_visualization(
        app_py,  # type: ignore
        "serverpy_graph.png",
        base_path=r"ai_workspace\agents\code_generators\v4\graphs",
    )

    # Example test inputs for server.js and server.py generation
    t_inputs = [
        {
            "question_html": """<pl-question-panel>\n  
            <p>A car is traveling along a straight road at a speed of {{params.initialSpeed}} {{params.unitsSpeed}}. 
            It sees a stop sign {{params.distanceToSign}} {{params.unitsDistance}} ahead and applies the brakes, coming to a complete stop just as it reaches the sign.</p>\n  <p>What is the car\'s constant acceleration during this process? Show your calculations.</p>\n</pl-question-panel>\n\n<pl-input-container>\n  
            <pl-number-input answers-name="initialSpeed" label="Initial Speed ({{params.unitsSpeed}})" />\n  <pl-number-input answers-name="distanceToSign" label="Distance to Stop Sign ({{params.unitsDistance}})" />\n</pl-input-container>\n\n<pl-number-input answers-name="acceleration" comparison="sigfig" digits="3" label="Acceleration (in {{params.unitsAcceleration}})"/>""",
        },
    ]

    # Stream output for server.js generation
    for t in t_inputs:
        for chunk in app.stream(t, stream_mode="updates"):  # type: ignore
            print(chunk)

    # Stream output for server.py generation
    for t in t_inputs:
        for chunk in app_py.stream(t, stream_mode="updates"):  # type: ignore
            print(chunk)
