from .questions.init import routes as questions_routes
from .ai_generation.code_generator import router as code_generation_router
from .startup import router as general_router
from .run_question_server import router as question_runner


routes = [
    code_generation_router,
    general_router,
    question_runner,
]

routes.extend(questions_routes)
