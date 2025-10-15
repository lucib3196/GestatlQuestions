from .crud.questions import router as question_router
from .auth.user import router as auth_router
from .ai_generation.code_generator import router as code_generation_router
from .general.startup import router as general_router
from .auth.authentication import router as auth_router
from .run_question_server import router as question_runner

routes = [
    question_router,
    auth_router,
    question_router,
    code_generation_router,
    general_router,
    auth_router,
    question_runner,
]
