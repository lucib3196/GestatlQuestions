from .questions.questions import router as question_router
from .ai_generation.code_generator import router as code_generation_router
from .startup import router as general_router
from .run_question_server import router as question_runner
from .questions.sync import router as question_loader

routes = [
    question_router,
    question_router,
    code_generation_router,
    general_router,
    question_runner,
    question_loader,
]
