# Standard library imports
import os
import uvicorn
from contextlib import asynccontextmanager

# Third-party imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRouter
from starlette import status
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Local application imports
from src.api.core.config import settings
from src.api.database.database import create_db_and_tables
from src.api.web.authentication import router as auth_router
from src.api.web.code_generator import router as code_generator_router
from src.api.web.user import router as user_route
from src.api.web.question_running import router as question_running_router
from src.api.web.question_crud import router as q_crud
from src.api.web.file_management import router as f_router

# from backend.src.api.web.refactor_file_management import router as file_router

# from backend_api.web.file_management import router as file_router
# from backend_api.web.local_questions import router as local_question_router
# from backend_api.web.db_questions import router as db_question_router


## Intializes the database
@asynccontextmanager
async def on_startup(app: FastAPI):
    create_db_and_tables()
    yield


routes = [
    auth_router,
    code_generator_router,
    user_route,
    q_crud,
    f_router,
    question_running_router,
]
print("This is the path", settings.QUESTIONS_PATH)


def add_routes(app: FastAPI, routes: list[APIRouter] = routes):
    for r in routes:
        app.include_router(r)


def get_application():
    app = FastAPI(title=settings.PROJECT_NAME, lifespan=on_startup)
    add_routes(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin) for origin in settings.BACKEND_CORS_ORIGINS
        ],  # allow specific frontend origins
        allow_credentials=True,  # allow cookies, Authorization headers
        allow_methods=["*"],  # allow all HTTP methods (GET, POST, etc.)
        allow_headers=["*"],  # allow all headers (including Authorization)
    )
    if not settings.QUESTIONS_PATH:
        raise ValueError("Cannot Find Local Path")
    print("This is the question path", settings.QUESTIONS_PATH)
    questions_dir = Path(settings.QUESTIONS_PATH).resolve()
    print(questions_dir)

    app.mount(
        f"/{questions_dir.name}",  # -> "/questions"
        StaticFiles(directory=questions_dir, html=False),
        name="questions",
    )
    print("Serving static files from:", questions_dir)

    # Define a custom OpenAPI schema that uses your token URL at /auth/login
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title=app.title,
            version="1.0.0",  # Update version as needed
            description="API documentation with OAuth2 security",
            routes=app.routes,
        )
        openapi_schema["components"]["securitySchemes"] = {
            "OAuth2PasswordBearer": {
                "type": "oauth2",
                "flows": {
                    "password": {
                        "tokenUrl": settings.AUTH_URL,
                        "scopes": {},
                    }
                },
            }
        }
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    return app


app = get_application()


@app.get("/")
@app.get("/startup", status_code=status.HTTP_200_OK)
def startup_connection():
    return {"message": "The API is LIVE!!"}


def main():

    uvicorn.run(
        "backend_api.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=False,
    )


if __name__ == "__main__":
    main()
