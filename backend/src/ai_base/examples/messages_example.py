from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from ..settings import get_settings


settings = get_settings()
n = 100
MODEL = settings.base_model.model
PROVIDER = settings.base_model.provider

model = init_chat_model(
    model=MODEL,
    model_provider=PROVIDER,
)

system_msg = SystemMessage("You are a helpful assistant.")
human_msg = HumanMessage("Hello, how are you?")

# Use with chat models
messages = [system_msg, human_msg]
response = model.invoke(messages)  # Returns AIMessage

print(f"First response \n\n{'*'*n}\n{response}\n\n")

# Also pass in as a dictionary
messages = [
    {"role": "system", "content": "You are a poetry expert"},
    {"role": "user", "content": "Write a haiku about spring"},
    {"role": "assistant", "content": "Cherry blossoms bloom..."},
]
response = model.invoke(messages)

print(f"Second response \n\n{'*'*n}\n\n{response}")
