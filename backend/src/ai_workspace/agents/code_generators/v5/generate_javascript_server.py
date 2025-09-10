# Standard library
from typing import Optional

# Third-party libraries
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, START, StateGraph
from langsmith import Client
from pydantic import BaseModel

# Local application
from .initializer import init_generation
from src.ai_workspace.models import CodeResponse
from src.ai_workspace.utils import (
    save_graph_visualization,
    inject_message,
    validate_llm_output,
)
from src.ai_workspace.retrievers import SemanticExamplesCSV


client = Client()

resources = init_generation(column_names=("question.html", "server.js"))
prompt_base = "server_js_template_base"
predefined_value_template = "server_add_predefined"
test_template = "server_test"
fast_llm = resources.fast_llm
base_llm = resources.base_llm

if isinstance(resources.q_retriver, SemanticExamplesCSV):
    q_retriever_js = resources.q_retriver
else:
    raise ValueError("Expected Retriever to be of type SemanticExampleCSV")


# Define State
class ServerState(BaseModel):
    question_html: str
    server_file: str = ""
    original_question: Optional[str] = None
    solution_guide: Optional[str] = None
    test_parameters: Optional[str] = None
    isAdaptive: bool = True


def generate_server_base(state: ServerState) -> ServerState:
    """Generates the javascript base code uses
    semantic search to look through a database for relavent examples as a guide
    this creates the base server file.
    """
    base_prompt = client.pull_prompt(prompt_base)

    # Apply the retriever to filter and build prompt
    q_retriever_js.set_filter({"isAdaptive": state.isAdaptive})
    prompt: ChatPromptTemplate = q_retriever_js.format_template(
        query=state.question_html, k=1, base_template=base_prompt
    )
    messages = prompt.format_prompt(question=state.question_html)

    chain = base_llm.with_structured_output(CodeResponse)

    if state.solution_guide:
        solution_prompt = f"""
            You are provided with the following solution guide. Use its reasoning, steps,
            and methodology as the primary reference for the JavaScript (server.js) implementation.
            Expand steps where necessary for clarity, but ensure the structure and logic of the
            JavaScript output closely follow the guide's approach.

            Solution Guide:
            {state.solution_guide}
        """
        messages = inject_message(messages, solution_prompt)

    result: CodeResponse = validate_llm_output(chain.invoke(messages), CodeResponse)

    return {"server_file": result.code}  # type: ignore


def add_predefined_values(state: ServerState):
    base_prompt: ChatPromptTemplate = client.pull_prompt(predefined_value_template)
    messages = base_prompt.format_prompt(
        code=state.server_file, question=state.original_question
    )
    chain = base_llm.with_structured_output(CodeResponse)
    result: CodeResponse = validate_llm_output(chain.invoke(messages), CodeResponse)
    return {"server_file": result.code}  # type: ignore


def add_test(state: ServerState):
    base_prompt: ChatPromptTemplate = client.pull_prompt(test_template)
    messages = base_prompt.format(
        original_question=state.original_question,
        question=state.server_file,
        parameters=state.test_parameters,
    )
    chain = base_llm.with_structured_output(CodeResponse)
    result: CodeResponse = validate_llm_output(chain.invoke(messages), CodeResponse)
    return {"server_file": result.code}  # type: ignore


def add_test_router(state: ServerState):
    if state.test_parameters:
        return "add_test"
    else:
        return END


# Construct the graph
workflow = StateGraph(ServerState)
workflow.add_node("generate_server_base_js", generate_server_base)  # type: ignore
workflow.add_node("add_predefined_values", add_predefined_values)  # type: ignore
workflow.add_node("add_test", add_test)

workflow.add_edge(START, "generate_server_base_js")
workflow.add_edge("generate_server_base_js", "add_predefined_values")
workflow.add_conditional_edges(
    "add_predefined_values", add_test_router, ["add_test", END]
)
workflow.add_edge("add_test", END)
app = workflow.compile()


if __name__ == "__main__":
    save_graph_visualization(
        app,  # type: ignore
        "serverjs_graph.png",
        base_path=r"ai_workspace\agents\code_generators\v5\graphs",
    )

    async def test():

        t_inputs = [
            {
                "question_html": """<pl-question-panel>\n  
    <p>A car is traveling along a straight road at a speed of {{params.initialSpeed}} {{params.unitsSpeed}}. 
    It sees a stop sign {{params.distanceToSign}} {{params.unitsDistance}} ahead and applies the brakes, coming to a complete stop just as it reaches the sign.</p>\n  
    <p>What is the car's constant acceleration during this process? Show your calculations.</p>\n
    </pl-question-panel>\n\n
    <pl-input-container>\n  
    <pl-number-input answers-name="initialSpeed" label="Initial Speed ({{params.unitsSpeed}})" />\n  
    <pl-number-input answers-name="distanceToSign" label="Distance to Stop Sign ({{params.unitsDistance}})" />\n
    </pl-input-container>\n\n
    <pl-number-input answers-name="acceleration" comparison="sigfig" digits="3" label="Acceleration (in {{params.unitsAcceleration}})"/>""",
                "original_question": "A car is traveling along a straight road at a speed of 20 m/s. It sees a stop sign 50 m ahead and applies the brakes, coming to a complete stop just as it reaches the sign. What is the car's constant acceleration during this process? Show your calculations.",
                "isAdaptive": True,
                "test_parameters": "initialSpeed: 20, unitsSpeed: m/s, distanceToSign: 50, unitsDistance: m, unitsAcceleration: m/s^2, correctAnswer: -4.0",
            }
        ]
        for t in t_inputs:
            async for chunk in app.astream(ServerState(**t), stream_mode="updates"):
                print(chunk)

    import asyncio

    asyncio.run(test())
