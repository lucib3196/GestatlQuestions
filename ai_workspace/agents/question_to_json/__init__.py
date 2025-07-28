from dotenv import load_dotenv
import os

load_dotenv()


from .question_to_json_agent import chain as question_to_json_chain
from .solution_to_json_agent import chain as solution_to_json_chain