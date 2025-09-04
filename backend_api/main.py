import os
import uuid
import uvicorn

from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, HTTPException, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from starlette import status
from pydantic import BaseModel
from firebase_admin import storage

# from .fb_config import db
from fastapi.openapi.utils import get_openapi

# Internal imports
from backend_api.core.config import settings
from backend_api.data.database import init_db

# Routers
from backend_api.web.authentication import router as auth_router

# from backend_api.web.file_management import router as file_router
# from backend_api.web.local_questions import router as local_question_router
from backend_api.web.code_generator import router as code_generator_router
from backend_api.web.user import router as user_route
from backend_api.web.question_running import router as question_running_router

# from backend_api.web.db_questions import router as db_question_router

from backend_api.web.question_crud import router as q_crud
from backend_api.web.file_management import router as file_router

# Define startup activity
# Define database and create on starup
# Set the database


@asynccontextmanager
async def on_startup(app: FastAPI):
    # Only initialize DB in dev/prod, not in tests
    if settings.ENV in ("dev", "prod"):
        init_db()
    yield


def get_application():
    app = FastAPI(title=settings.PROJECT_NAME, lifespan=on_startup)

    # Add routes
    routes = [
        auth_router,
        code_generator_router,
        user_route,
        q_crud,
        file_router,
        question_running_router,
    ]
    for r in routes:
        app.include_router(r)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin) for origin in settings.BACKEND_CORS_ORIGINS
        ],  # allow specific frontend origins
        allow_credentials=True,  # allow cookies, Authorization headers
        allow_methods=["*"],  # allow all HTTP methods (GET, POST, etc.)
        allow_headers=["*"],  # allow all headers (including Authorization)
    )

    # Create a static mount for images
    app.mount(
        "/local_questions",
        StaticFiles(directory="local_questions"),
        name="local_questions",
    )

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
