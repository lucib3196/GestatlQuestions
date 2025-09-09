from langchain_openai import ChatOpenAI
from langsmith import Client
from .models import Solution

langsmith_client = Client()
prompt = langsmith_client.pull_prompt("solution_qmeta")
model = ChatOpenAI(model="gpt-4o-mini").with_structured_output(Solution)
chain = prompt | model


if __name__ == "__main__":
    q_input = r"""<pl-solution-panel>
    <pl-hint level="1" data-type="text">
        To find the car's constant acceleration, we can use the kinematic equation:  $$ v^2 = u^2 + 2a s $$, where  $$ v $$ is the final speed (0 m/s, since the car stops),  $$ u $$ is the initial speed,  $$ a $$ is the acceleration, and  $$ s $$ is the distance to the stop sign.
    </pl-hint>
    <pl-hint level="2" data-type="text">
        Rearranging the equation to solve for acceleration, we get:  $$ a = \frac{v^2 - u^2}{2s} $$. 
    </pl-hint>
    <pl-hint level="3" data-type="text">
        Substituting the values:  $$ v = 0 \, \text{m/s}, \quad u = [[params.initialSpeed]] \, [[params.unitsSpeed]], \quad s = [[params.distanceToSign]] \, [[params.unitsDistance]]. $$
    </pl-hint>
    <pl-hint level="4" data-type="text">
        Now, plugging in these values, we can calculate the acceleration as follows:  $$ a = \frac{0^2 - ([[params.initialSpeed]])^2}{2 \times [[params.distanceToSign]]}. $$
    </pl-hint>
    <pl-hint level="5" data-type="text">
        Therefore, the car's constant acceleration is: $$ a = \frac{-([[params.initialSpeed]])^2}{2 \times [[params.distanceToSign]]} = [[params.correct_answers.acceleration]] \, [[params.unitsAcceleration]]. $$
    </pl-hint>
</pl-solution-panel>
"""
    response = chain.invoke({"question": q_input})
