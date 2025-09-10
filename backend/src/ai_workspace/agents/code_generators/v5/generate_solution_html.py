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

resources = init_generation(
    name="question html", column_names=("question.html", "solution.html")
)
prompt_base = "solution_html_template"
fast_llm = resources.fast_llm
base_llm = resources.base_llm
if isinstance(resources.q_retriver, SemanticExamplesCSV):
    q_retriever = resources.q_retriver
else:
    raise TypeError("Expected SemanticExamplesCSV")


class State(BaseModel):
    question_html: str
    solution_guide: Optional[str] = None
    solution_html: str = ""
    isAdaptive: bool = True


def generate_solution_html(state: State):
    base_prompt = client.pull_prompt(prompt_base)

    q_retriever.set_filter({"isAdaptive": state.isAdaptive})
    prompt_result = q_retriever.format_template(
        query=state.question_html, k=3, base_template=base_prompt
    )
    if isinstance(prompt_result, str):
        prompt: ChatPromptTemplate = ChatPromptTemplate.from_template(prompt_result)
    else:
        prompt: ChatPromptTemplate = prompt_result
    messages = prompt.format_prompt(question=state.question_html).to_messages()

    if state.solution_guide:
        additional_instructions = (
            "You are provided with a solution guide. "
            "When generating the solution HTML file, ensure your response closely follows the steps, logic, and details outlined in the guide. "
            "Integrate the guide's reasoning and calculations into the solution HTML as appropriate."
        )
        messages = inject_message(messages, content=additional_instructions)
    chain = base_llm.with_structured_output(CodeResponse)
    result: CodeResponse = validate_llm_output(chain.invoke(messages), CodeResponse)
    return {"solution_html": result.code}  # type: ignore


workflow = StateGraph(State)
workflow.add_node("generate_solution_html", generate_solution_html)  # type: ignore


workflow.add_edge(START, "generate_solution_html")
workflow.add_edge("generate_solution_html", END)
app = workflow.compile()

if __name__ == "__main__":
    save_graph_visualization(
        app,  # type: ignore
        "solution_html.png",
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
                "isAdaptive": True,
            }
        ]
        for t in t_inputs:
            async for chunk in app.astream(State(**t), stream_mode="updates"):
                print(chunk)

    import asyncio

    asyncio.run(test())
