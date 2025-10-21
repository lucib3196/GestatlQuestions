from langchain.chat_models import init_chat_model
from ..settings import get_settings
import numpy as np

settings = get_settings()
MODEL = settings.base_model.model
PROVIDER = settings.base_model.provider

model = init_chat_model(
    model=MODEL,
    model_provider=PROVIDER,
)

def get_weather(location: str) -> str:
    # Dummy data
    val = np.random.randint(50, 80)  # Random value for the weather

    return f"The weather in {location} is {val}"


model_with_tools = model.bind_tools([get_weather])
response = model_with_tools.invoke("What's the weather in Paris?")

for tool_call in response.tool_calls:  # type: ignore
    print(f"Tool: {tool_call['name']}")
    print(f"Args: {tool_call['args']}")
    print(f"ID: {tool_call['id']}")
