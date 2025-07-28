from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel
from .code_generator import (
    CodeGenInput,
    CodeGenOutput,
    compiled_graph as code_generator,
)
from ai_workspace.utils import save_graph_visualization
from ai_workspace.agents.question_to_json import (
    solution_to_json_chain,
    question_to_json_chain,
)
from typing import List, Optional, Literal
from ai_workspace.agents.question_to_json.models import QuestionBase, Solution
from backend_api.model.questions_models import QuestionMetaNew
from ai_workspace.models import Question
from ai_workspace.utils import to_serializable

# StateModels


class State(CodeGenOutput):
    questionRender: Optional[List[QuestionBase]] = None
    solutionRender: Optional[Solution] = None
    qtype: Optional[List[Literal["numeric", "multiple_choice"]]] = None


class OutputState(CodeGenOutput):
    qmeta: QuestionMetaNew


# Node Functions
def generate_code(state: CodeGenInput) -> State:
    response = code_generator.invoke(state)
    return response  # type: ignore


def format_question(state: State):
    response = question_to_json_chain.invoke({"question": state.files.question_html})
    response = to_serializable(response)
    return {
        "questionRender": response.get("questionBase"),
        "qtype": response.get("qtype", []),
    }


def format_solution(state: State):
    return {
        "solutionRender": to_serializable(
            solution_to_json_chain.invoke({"question": state.files.solution_html})
        )
    }


def generate_qmeta(state: State) -> OutputState:
    qmeta = QuestionMetaNew(
        rendering_data=state.questionRender,  # type: ignore
        solution_render=state.solutionRender,
        title=state.q_metadata.title,
        topic=state.q_metadata.topic,
        relevantCourses=state.q_metadata.relevantCourses,
        isAdaptive=(
            state.q_metadata.isAdaptive
            if isinstance(state.q_metadata.isAdaptive, (str, bool))
            else False  # or "False" depending on what's expected
        ),
        language=["javascript", "python"],
        ai_generated=True,
        qtype=state.qtype,
    )
    return {"qmeta": qmeta}  # type: ignore


graph = StateGraph(State, input_schema=CodeGenInput, output_schema=OutputState)
graph.add_node(
    "generate_code",
    generate_code,  # type: ignore
)
graph.add_node("format_question", format_question)
graph.add_node("format_solution", format_solution)
graph.add_node("generate_qmeta", generate_qmeta)


graph.add_edge(START, "generate_code")
graph.add_edge("generate_code", "format_question")
graph.add_edge("generate_code", "format_solution")
graph.add_edge("format_question", "generate_qmeta")
graph.add_edge("format_solution", "generate_qmeta")
graph.add_edge("generate_qmeta", END)

compiled_graph = graph.compile()


def main():
    """
    Main function to visualize and run the code generation pipeline.
    """
    save_graph_visualization(
        compiled_graph,  # type: ignore
        filename="CodeGenQmeta.png",
        base_path=r"ai_workspace/agents/code_generators/v4/graphs",
    )
    question = "A car is traveling along a straight road at 60 mph; calculate distance after 4 hours"
    input_state = CodeGenInput(
        question_payload=Question(question=question),  # type: ignore
        initial_metadata=None,
    )  # type: ignore
    for chunk in compiled_graph.stream(input_state, stream_mode="updates"):
        print(chunk)


if __name__ == "__main__":
    main()
