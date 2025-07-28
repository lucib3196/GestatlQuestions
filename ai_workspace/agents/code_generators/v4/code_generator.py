from pydantic import BaseModel, Field
from typing import Annotated, Optional, Dict, Any, List
import operator
from langgraph.graph import END, START, StateGraph
from ai_workspace.models import Question, FilesData
from ai_workspace.utils import keep_first, keep_new, merge_files_data

from .metadata_gen import MetadataState, MetadataInput
from .metadata_gen import compiled_graph as metadata_chain
from .code_review import CodeReview, code_review, code_fix
from .question_html import app as question_html_chain, State as QHtmlState
from .server_files import app as js_chain, app_py as py_chain, State as ServerStateInput
from .solution_html import app as solution_chain, State as SolutionInputState
from langchain_openai import ChatOpenAI
from ai_workspace.utils import to_serializable, save_graph_visualization

# ────────────────────────────────────────────────────────────────────────────────
# Constants
# ────────────────────────────────────────────────────────────────────────────────
FASTLLM = "gpt-4o-mini"
LONGCONTEXTLLM = "o3-mini-2025-01-31"

fast_llm = ChatOpenAI(model=FASTLLM)
long_context = ChatOpenAI(model=LONGCONTEXTLLM)

MAX_ITERATIONS = 3


# Helper
def extract_question_html(files: Optional[FilesData | Dict[str, str]]) -> str:
    """
    Helper to extract question_html from files.
    """
    if files is not None:
        if isinstance(files, dict):
            return files.get("question_html", "")
        return getattr(files, "question_html", "")
    return ""


def get_file_attr(files, key):
    if isinstance(files, dict):
        return files.get(key, "")
    return getattr(files, key, "")


# State Models
class CodeGenInput(BaseModel):
    """
    Input state for the code generation pipeline.
    """

    question_payload: Annotated[Question, keep_first] = Field(
        ..., description="The question to be processed."
    )
    initial_metadata: Annotated[Optional[dict], keep_first] = Field(
        None, description="Metadata about who is running the generators."
    )


class CodeGenState(BaseModel):
    """
    State model representing the current state in the code generation pipeline.
    """

    question_payload: Annotated[Question, keep_first] = Field(
        ..., description="The question to be processed."
    )
    initial_metadata: Annotated[Optional[dict], keep_first] = Field(
        None, description="Metadata about who is running the generators."
    )
    question_metadata: Annotated[MetadataState, keep_new] = Field(
        Field(default_factory=MetadataState),
        description="Metadata related to the question.",
    )
    files: Annotated[FilesData | Dict[str, Any], merge_files_data] = Field(
        default_factory=FilesData, description="The files to be generated."
    )
    is_adaptive: Annotated[bool, keep_first] = Field(
        default=False, description="Flag indicating if the question is adaptive."
    )
    code_review_message: Annotated[List[CodeReview], operator.add] = Field(
        default_factory=list, description="Code Review Messages"
    )
    iterations: int = Field(0, description="Number of iterations so far.")


class CodeGenOutput(BaseModel):
    question_payload: Annotated[Question, keep_first]
    metadata: Annotated[dict, keep_first]
    files: Annotated[FilesData, merge_files_data]
    # The other metadata are seperated this needs to be fixed
    q_metadata: Annotated[MetadataState, keep_new]
    initial: Annotated[Optional[dict], keep_new]


# Node Functions
def extract_question_metadata(state: CodeGenInput) -> CodeGenState:
    """
    Extracts metadata for the question using the metadata_chain.
    """
    metadata_input = MetadataInput(question=state.question_payload.question)
    result = metadata_chain.invoke(metadata_input)
    return {
        "question_metadata": result,
        "is_adaptive": result.get("isAdaptive"),
    }  # type: ignore


def generate_question_html(state: CodeGenState) -> CodeGenState:
    """
    Generates the HTML representation of the question.
    """
    html_input = QHtmlState(
        question=state.question_payload.question, isAdaptive=state.is_adaptive
    )
    result = question_html_chain.invoke(html_input)
    updated_files = FilesData(question_html=result.get("qfile", ""))
    return {"files": updated_files.model_dump()}  # type: ignore


def generate_server_js_file(state: CodeGenState) -> CodeGenState:
    """
    Generates the server-side JavaScript file.
    """
    question_html = extract_question_html(state.files)
    js_input = ServerStateInput(
        question_html=question_html,
        solution_guide=state.question_payload.solution_as_str,
        isAdaptive=state.is_adaptive,
    )
    result = js_chain.invoke(js_input)
    updated_files = FilesData(server_js=result.get("server_file", ""))
    return {"files": updated_files.model_dump()}  # type: ignore


def generate_server_py_file(state: CodeGenState) -> CodeGenState:
    """
    Generates the server-side Python file.
    """
    question_html = extract_question_html(state.files)
    py_input = ServerStateInput(
        question_html=question_html,
        solution_guide=state.question_payload.solution_as_str,
        isAdaptive=state.is_adaptive,
    )
    result = py_chain.invoke(py_input)
    updated_files = FilesData(server_py=result.get("server_file", ""))
    return {"files": updated_files.model_dump()}  # type: ignore


def generate_solution_html_file(state: CodeGenState) -> CodeGenState:
    """
    Generates the HTML for the solution.
    """
    question_html = extract_question_html(state.files)
    solution_input = SolutionInputState(
        question=question_html,
        solution=state.question_payload.solution_as_str,
        isAdaptive=state.is_adaptive,
    )
    result = solution_chain.invoke(solution_input)
    updated_files = FilesData(solution_html=result.get("qfile", ""))
    return {"files": updated_files.model_dump()}  # type: ignore


def adaptive_code_review(state: CodeGenState) -> CodeGenState:
    """
    Combines outputs for adaptive questions.
    """

    code_blocks = f"""
    The following is the code to review
    question.html: {get_file_attr(state.files, 'question_html')}
    solution.html: {get_file_attr(state.files, 'solution_html')}
    server.js: {get_file_attr(state.files, 'server_js')}
    server.py: {get_file_attr(state.files, 'server_py')}
    """

    result = code_review.invoke({"input": code_blocks})
    iterations = state.iterations + 1
    return {"code_review_message": [result], "iterations": iterations}  # type: ignore


def modify_code(state: CodeGenState) -> CodeGenState:
    """
    Applies code modifications based on the latest code review feedback.
    """
    last_review = state.code_review_message[-1].files_to_modify
    all_files = state.files.model_dump() if hasattr(state.files, "model_dump") else dict(state.files)  # type: ignore

    # Map review file names to keys in all_files
    filename_map = {
        "question_html": "question_html",
        "solution_html": "solution_html",
        "server_js": "server_js",
        "server.py": "server_py",
        "server.js": "server_js",
        "server_py": "server_py",
        "question.html": "question_html",
        "solution.html": "solution_html",
        "server.js": "server_js",
        "server.py": "server_py",
    }

    for file_mod in last_review:
        filename = file_mod.file_name
        approach = file_mod.approach
        # Normalize filename to match keys in all_files
        file_key = filename_map.get(filename, filename)
        original_code = all_files.get(file_key, "")

        # Skip modification if no approach or original code is empty
        if not approach or not original_code:
            continue

        result = code_fix.invoke({"approach": approach, "code": original_code})
        # Only update if code was actually returned
        updated_code = result.code  # type: ignore
        all_files[file_key] = updated_code

    return {"files": all_files}  # type: ignore


def finalize_package(state: CodeGenState) -> CodeGenOutput:
    # Serialize and combine metadata
    metadata = {}
    if state.initial_metadata:
        metadata.update(to_serializable(state.initial_metadata))
    if state.question_metadata:
        metadata.update(to_serializable(state.question_metadata))

    # Merge metadata into files
    files = state.files
    if isinstance(files, dict):
        files = FilesData(**files)
    files.metadata = metadata

    return CodeGenOutput(
        question_payload=state.question_payload,
        metadata=metadata,
        files=files,
        q_metadata=state.question_metadata,
        initial=state.initial_metadata,
    )


def route_server_file_generation(state: CodeGenState) -> List[str]:
    """
    Determines which server files (JS/PY) to generate based on adaptivity.
    """
    return (
        ["generate_server_js", "generate_server_py"] if bool(state.is_adaptive) else []
    )


def route_solution_generation(state: CodeGenState) -> str:
    """
    Determines the next step after generating solution HTML.
    """
    return "adaptive_code_review" if bool(state.is_adaptive) else END


def decide_to_modify(state: CodeGenState) -> str:
    if state.code_review_message[-1].grade == "yes" and state.iterations < MAX_ITERATIONS:  # type: ignore
        return "modify_code"
    else:
        return "finalize_package"


def decied_to_review(state: CodeGenState):
    if state.iterations < MAX_ITERATIONS:
        return "adaptive_code_review"
    else:
        return "finalize_package"


graph = StateGraph(CodeGenState, input_schema=CodeGenInput, output_schema=CodeGenOutput)

# Register nodes
graph.add_node(
    "extract_question_metadata",
    extract_question_metadata,  # type: ignore
)
graph.add_node("generate_question_html", generate_question_html)
graph.add_node("generate_server_js", generate_server_js_file)
graph.add_node("generate_server_py", generate_server_py_file)
graph.add_node(
    "generate_solution_html",
    generate_solution_html_file,
)
graph.add_node("adaptive_code_review", adaptive_code_review)
graph.add_node("modify_code", modify_code)

graph.add_node("finalize_package", finalize_package)

# Register edges
graph.add_edge(START, "extract_question_metadata")
graph.add_edge("extract_question_metadata", "generate_question_html")
graph.add_edge("generate_question_html", "generate_solution_html")

# Conditional: generate server files if adaptive
graph.add_conditional_edges(
    "generate_question_html",
    route_server_file_generation,  # type: ignore
    ["generate_server_js", "generate_server_py"],
)

# Server file generation leads to code review
graph.add_edge("generate_server_js", "adaptive_code_review")
graph.add_edge("generate_server_py", "adaptive_code_review")

# Conditional: after solution HTML, either combine outputs or end
graph.add_conditional_edges(
    "generate_solution_html",
    route_solution_generation,
    ["adaptive_code_review", "finalize_package"],
)

# Code review can lead to modification or end
graph.add_conditional_edges(
    "adaptive_code_review",
    decide_to_modify,
    ["modify_code","finalize_package"],
)
graph.add_conditional_edges(
    "modify_code",
    decied_to_review,
    ["adaptive_code_review","finalize_package"],
)


# If code is modified, process ends (can be extended for further iterations)
graph.add_edge("adaptive_code_review", "finalize_package")
graph.add_edge("finalize_package", END)
compiled_graph = graph.compile()


# ────────────────────────────────────────────────────────────────────────────────
# Main Entrypoint
# ────────────────────────────────────────────────────────────────────────────────
def main():
    """
    Main function to visualize and run the code generation pipeline.
    """
    save_graph_visualization(
        compiled_graph,  # type: ignore
        filename="CodeGeneratorV3.png",
        base_path=r"ai_workspace/agents/code_generators/v4/graphs",
    )
    question = "A car is traveling along a straight road at 60 mph; calculate distance after 4 hours"
    input_state = CodeGenInput(
        question_payload=Question(question=question),  # type: ignore
        initial_metadata=None,
    )  # type: ignore
    for chunk in compiled_graph.stream(input_state, stream_mode="updates"):
        if chunk.get("modify_code", ""):
            print(chunk)


if __name__ == "__main__":
    main()
