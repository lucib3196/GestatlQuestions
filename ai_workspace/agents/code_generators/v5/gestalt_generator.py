from typing import List, Optional, Annotated

from pydantic import BaseModel
from langgraph.graph import END, START, StateGraph

from ai_workspace.models import Question
from ai_workspace.utils import (
    save_graph_visualization,
    validate_llm_output,
)

from .generate_metadata import (
    compiled_graph as metadata_graph,
    MetadataInput as Metadata,
)
from .generate_question_html import (
    app as generate_question_html_graph,
    State as QHtmlState,
)
from .generate_javascript_server import (
    app as generate_server_js_graph,
    ServerState as JsServer,
)
from .generate_python_server import (
    app as generate_server_py_graph,
    ServerState as PyServer,
)
from .generate_solution_html import (
    app as generate_solution_html_graph,
    State as SHtml,
)


def normalize_bool(val) -> bool:
    return val == True or (isinstance(val, str) and val.lower() == "true")


def merge_files(existing: dict, new: dict) -> dict:
    existing.update(new)
    return existing


class CodeGen(BaseModel):
    question_payload: Question
    files_data: Annotated[dict, merge_files] = {}
    metadata: Optional[Metadata] = None


def generate_question_metadata(state: CodeGen):
    result: Metadata = validate_llm_output(
        metadata_graph.invoke(input=Metadata(question=state.question_payload.question)),
        Metadata,
    )
    return {"metadata": result}


def generate_question_html(state: CodeGen):
    result: QHtmlState = validate_llm_output(
        generate_question_html_graph.invoke(
            input=QHtmlState(
                question=state.question_payload.question,
                isAdaptive=(
                    normalize_bool(state.metadata.isAdaptive)
                    if state.metadata
                    else True
                ),
            )
        ),
        QHtmlState,
    )
    files_data = {"question.html": result.question_html}
    return {"files_data": files_data}


def generate_solution_html(state: CodeGen):
    result: SHtml = validate_llm_output(
        generate_solution_html_graph.invoke(
            input=SHtml(
                question_html=state.files_data.get("question.html", ""),
                isAdaptive=(
                    normalize_bool(state.metadata.isAdaptive)
                    if state.metadata
                    else True
                ),
            )
        ),
        SHtml,
    )
    files_data = {"solution.html": result.solution_html}
    return {"files_data": files_data}


def generate_server_js(state: CodeGen):
    result: JsServer = validate_llm_output(
        generate_server_js_graph.invoke(
            JsServer(
                question_html=state.files_data.get("question.html", ""),
                original_question=state.question_payload.question,
                solution_guide=state.question_payload.solution_as_str,
                test_parameters=(
                    state.question_payload.format_params
                    if state.question_payload.correct_answers
                    else None
                ),
            )
        ),
        JsServer,
    )
    files_data = {"server.js": result.server_file}
    return {"files_data": files_data}


def generate_server_py(state: CodeGen):
    result: PyServer = validate_llm_output(
        generate_server_py_graph.invoke(
            PyServer(
                question_html=state.files_data.get("question.html", ""),
                original_question=state.question_payload.question,
                solution_guide=state.question_payload.solution_as_str,
                test_parameters=(
                    state.question_payload.format_params
                    if state.question_payload.correct_answers
                    else None
                ),
            )
        ),
        PyServer,
    )
    files_data = {"server.py": result.server_file}
    return {"files_data": files_data}


def route_server_file_generation(state: CodeGen) -> List[str]:
    """
    Determines which server files (JS/PY) to generate based on adaptivity.
    """
    return (
        ["generate_server_js", "generate_server_py"]
        if bool(state.metadata.isAdaptive if state.metadata else False)
        else []
    )


graph = StateGraph(CodeGen)
graph.add_node(
    "generate_question_metadata",
    generate_question_metadata,  # type: ignore
)
graph.add_node("generate_question_html", generate_question_html)
graph.add_node("generate_solution_html", generate_solution_html)
graph.add_node("generate_server_js", generate_server_js)
graph.add_node("generate_server_py", generate_server_py)

graph.add_edge(START, "generate_question_metadata")
graph.add_edge("generate_question_metadata", "generate_question_html")
graph.add_edge("generate_question_html", "generate_solution_html")

graph.add_conditional_edges(
    "generate_question_html",
    route_server_file_generation,  # type: ignore
    ["generate_server_js", "generate_server_py"],
)

graph.add_edge("generate_server_js", END)
graph.add_edge("generate_server_py", END)
graph.add_edge("generate_solution_html", END)
app = graph.compile()


def main():
    """
    Main function to visualize and run the code generation pipeline.
    """
    save_graph_visualization(
        app,  # type: ignore
        filename="code_generator_v5.png",
        base_path=r"ai_workspace\agents\code_generators\v5\graphs",
    )
    question = "A car is traveling along a straight road at 60 mph; calculate distance after 4 hours"
    input_state = CodeGen(
        question_payload=Question(question=question),  # type: ignore
    )  # type: ignore
    for chunk in app.stream(input_state, stream_mode="updates"):
        print(chunk)
        print("/n")


if __name__ == "__main__":
    main()
