from langchain_openai import ChatOpenAI
from langsmith import Client
from typing import List, Optional
from pydantic import BaseModel
from .models import QuestionBase, QuestionPayload
from langgraph.graph import END, StateGraph, START
import json

# Constants
FASTLLM = "gpt-4o-mini"
LONGCONTEXTLLM = "o3-mini-2025-01-31"
# Pulling Prompts
langsmith_client = Client()
prompt = langsmith_client.pull_prompt("question_input_analysis")


# Defining schema
class QmetaResponse(BaseModel):
    qmeta: List[QuestionBase]


# Main LLM Call
model = ChatOpenAI(model=FASTLLM).with_structured_output(QmetaResponse)
question_chain = prompt | model


class InputState(BaseModel):
    question: str
    info_json: dict
    qmeta: None


class IntermediateState(BaseModel):
    question: str
    info_json: dict
    qmeta: List[QuestionBase]


class FinalState(BaseModel):
    question: str
    payload: QuestionPayload


def convert_question(state: InputState) -> IntermediateState:
    result = question_chain.invoke({"question": state.question})
    state.qmeta = result
    return result


def update_metadata(state: IntermediateState) -> FinalState:
    data = state.info_json
    if not isinstance(data, dict):
        data = json.loads(data)

    # Extract fields
    title = data.get("title", "Untitled")
    topic = data.get("topic", [])
    tags = data.get("tags", [])
    isAdaptive = data.get("isAdaptive", "false")
    createdBy = data.get("createdBy", "")

    if isinstance(topic, str):
        topic = topic.split(",")

    payload = QuestionPayload(
        question=state.question,
        questionBase=state.qmeta,
        title=title,
        topic=topic,
        relevantCourses=[],
        tags=tags,
        isAdaptive=isAdaptive,
        createdBy=createdBy,
    )
    return {"payload": payload}  # type: ignore


workflow = StateGraph(FinalState, input=InputState, output=FinalState)  # type: ignore
workflow.add_node("convert_question", convert_question)
workflow.add_node("update_metadata", update_metadata)  # type: ignore


workflow.add_edge(START, "convert_question")
workflow.add_edge("convert_question", "update_metadata")
workflow.add_edge("update_metadata", END)

app = workflow.compile()

if __name__ == "__main__":
    q_inputs = [
        # 1️⃣ Original question + number input
        r"""<pl-question-panel>
    <p> Consider a glass window with thickness $ [[params.thickness]] [[params.unitsDist]] $, outside surface temperature $ [[params.T_outside]] [[params.unitsTemperature]] $, and inside surface temperature $ [[params.T_inside]] [[params.unitsTemperature]] $.  
    Determine the heat loss through the window with height $ [[params.height]] [[params.unitsDist]] $ and width $ [[params.width]] [[params.unitsDist]] $. Thermal conductivity of glass is $ [[params.k]] [[params.unitsThermalConductivity]] $.</p>
</pl-question-panel>

<pl-number-input answers-name="heatLoss" comparison="sigfig" digits="3" label="Heat Loss [[params.unitHeat]] = "></pl-number-input>
""",
        # 2️⃣ Second standalone question + number input
        r"""<pl-question-panel>
    <p> A cylindrical rod of length $ [[params.length]] [[params.unitsDist]] $ and cross-sectional area $ [[params.area]] [[params.unitsArea]] $ has one end held at $ [[params.T_hot]] [[params.unitsTemperature]] $ and the other at $ [[params.T_cold]] [[params.unitsTemperature]] $.  
    Calculate the steady-state rate of heat conduction through the rod. Thermal conductivity is $ [[params.k]] [[params.unitsThermalConductivity]] $.</p>
</pl-question-panel>

<pl-number-input answers-name="heatRate" comparison="sigfig" digits="3" label="Heat Conduction Rate [[params.unitHeatRate]] = "></pl-number-input>
""",
        # 3️⃣ Multipart question: two panels + inputs in one
        r"""<pl-question-panel>
    <p> (a) Consider a glass window with thickness $ [[params.thickness]] [[params.unitsDist]] $, outside surface temperature $ [[params.T_outside]] [[params.unitsTemperature]] $, and inside surface temperature $ [[params.T_inside]] [[params.unitsTemperature]] $.  
    Determine the heat loss through the window with height $ [[params.height]] [[params.unitsDist]] $ and width $ [[params.width]] [[params.unitsDist]] $. Thermal conductivity of glass is $ [[params.k]] [[params.unitsThermalConductivity]] $.</p>
</pl-question-panel>

<pl-number-input answers-name="partA_heatLoss" comparison="sigfig" digits="3" label="(a) Heat Loss [[params.unitHeat]] = "></pl-number-input>

<pl-question-panel>
    <p> (b) A cylindrical rod of length $ [[params.length]] [[params.unitsDist]] $ and cross-sectional area $ [[params.area]] [[params.unitsArea]] $ has one end held at $ [[params.T_hot]] [[params.unitsTemperature]] $ and the other at $ [[params.T_cold]] [[params.unitsTemperature]] $.  
    Calculate the steady-state rate of heat conduction through the rod. Thermal conductivity is $ [[params.k]] [[params.unitsThermalConductivity]] $.</p>
</pl-question-panel>

<pl-number-input answers-name="partB_heatRate" comparison="sigfig" digits="3" label="(b) Heat Conduction Rate [[params.unitHeatRate]] = "></pl-number-input>
""",
    ]

    for t in q_inputs:
        for chunk in app.stream(
            input=InputState(question=t, info_json={}, qmeta=None),
            stream_mode="updates",
        ):
            print(chunk)
            print("\n")
