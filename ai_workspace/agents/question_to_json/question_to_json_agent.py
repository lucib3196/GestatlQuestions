from langchain_openai import ChatOpenAI
from langsmith import Client
from ai_workspace.models import QuestionBase
from typing import Literal
from pydantic import BaseModel, Field
from typing import List


langsmith_client = Client()
prompt = langsmith_client.pull_prompt("new_question_render")


class Response(BaseModel):
    questionBase: List[QuestionBase]
    qtype: List[Literal["multiple-choice", "numeric"]] = Field(
        description="The type of inputs the question has can be multiple"
    )

chain = prompt | ChatOpenAI(model="gpt-4o-mini").with_structured_output(Response)


if __name__ == "__main__":
    q_input = r"""<<pl-question-panel>
    <p>A robotics competition involves programming an autonomous robot to complete a series of tasks:</p>
    <p>Part 1: The robot must travel a distance of [[params.distance]] [[params.unitsDist]] in a straight line. Enter the minimum time (in seconds) required if its maximum speed is [[params.maxSpeed]] [[params.unitsSpeed]].</p>
    <p>Calculate the time taken after substituting the values.</p>
    </pl-question-panel>
    <pl-number-input answers-name="time" comparison="exact" digits="2" label="Minimum time (in seconds)"></pl-number-input>

    <pl-question-panel>
    <p>Part 2: The robot must pick up an object and place it in one of three bins. Which bin should the robot choose if the object is metallic?</p>
    <ul>
        <li>A) Red bin (plastic)</li>
        <li>B) Blue bin (metal)</li>
        <li>C) Green bin (paper)</li>
    </ul>
    </pl-question-panel>
    <pl-multiple-choice answers-name="bin_choice" weight="1">
    <pl-answer correct="false">Red bin (plastic)</pl-answer>
    <pl-answer correct="true">Blue bin (metal)</pl-answer>
    <pl-answer correct="false">Green bin (paper)</pl-answer>
    </pl-multiple-choice>

    <pl-question-panel>
    <p>Part 3: After sorting, the robot must rotate [[params.angle]] degrees to face the next task. Enter the angle (in degrees) the robot must turn if it starts facing north and needs to face east.</p>
    </pl-question-panel>
    <pl-number-input answers-name="rotation_angle" comparison="exact" digits="0" label="Angle (in degrees)"></pl-number-input>
    """
    response = chain.invoke({"question": q_input, "solution": None})
    print(response)
