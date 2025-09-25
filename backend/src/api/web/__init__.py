from .crud.questions import router as question_router
from .user import router as auth_router
from .question_running import router as question_running
from .ai_generation.code_generator import router as code_generation_router
from .general.startup import router as general_router
routes = [question_router, auth_router, question_router, code_generation_router, general_router]