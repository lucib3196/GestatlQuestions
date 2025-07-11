from langchain_openai import ChatOpenAI
from langsmith import Client
from .models import QuestionBase

langsmith_client = Client()
prompt = langsmith_client.pull_prompt("question_input_analysis")
q_input = r"""<pl-question-panel>
    <p> Consider a glass window with thickness $ [[params.thickness]] [[params.unitsDist]] $, outside surface temperature $ [[params.T_outside]] [[params.unitsTemperature]] $, and inside surface temperature $ [[params.T_inside]] [[params.unitsTemperature]] $.  
    Determine the heat loss through the window with height $ [[params.height]] [[params.unitsDist]] $ and width $ [[params.width]] [[params.unitsDist]] $. Thermal conductivity of glass is $ [[params.k]] [[params.unitsThermalConductivity]] $.</p>
   
</pl-question-panel>

<pl-number-input answers-name="heatLoss" comparison="sigfig" digits="3" label="Heat Loss [[params.unitHeat]] = "></pl-number-input>
"""

model = ChatOpenAI(model="gpt-4o-mini").with_structured_output(QuestionBase)
chain = prompt | model
response = chain.invoke({"question": q_input})
print(response)
