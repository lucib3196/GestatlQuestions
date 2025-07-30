import logging
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

from firebase_admin import storage

from typing import Annotated

from .fb_config import db

# Routers
from backend_api.web.authentication import router
from backend_api.web.file_management import router as file_router
from backend_api.web.local_questions import router as local_question_router
from backend_api.web.code_generator import router as code_generator_router
from backend_api.data.database import create_db_and_tables
from backend_api.web.user import router as user_route


# Define startup activity
# Define database and create on starup
@asynccontextmanager
async def on_startup(app: FastAPI):
    create_db_and_tables()
    yield


# Routers
app = FastAPI(lifespan=on_startup)
routes = [router, code_generator_router, file_router, local_question_router, user_route]
for r in routes:
    app.include_router(r)

# Origins add more as needed
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # allow specific frontend origins
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


# Authentication

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    email: str | None = None
    fullname: str | None = None
    disabled: bool | None = None


def fake_decode_token(token):
    return User(
        username=token + "fakedecoded", email="john@example.com", fullname="John Doe"
    )


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    return user


@app.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}


class Question(BaseModel):
    title: str
    content_url: str  # URL to uploaded file


class Assign(BaseModel):
    reviewer_id: str


@app.post("/questions/", response_model=dict)
async def create_question(q: Question):
    bucket = storage.bucket()
    blob = bucket.blob("question.html")
    blob.upload_from_string("some content")
    qid = str(uuid.uuid4())
    blob.make_public()

    doc = {
        "id": qid,
        "title": q.title,
        "files": {"filename": "question.html", "url": blob.public_url},
        "content_url": q.content_url,
        "status": "unassigned",
        "assigned_to": None,
        "versions": [],
    }
    db.collection("questions").document(qid).set(doc)
    return {"id": qid, "status": "unassigned"}


@app.post("/questions/{qid}/edit")
async def edit_questions(qid: str):
    doc_ref = db.collection("questions").document(qid)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(404, "Question not Found")
    data = doc
    print(data)
    return {"files": data}


@app.post("/questions/{qid}/assing")
async def assign_question(qid: str, a: Assign):
    doc_ref = db.collection("questions").document(qid)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(404, "Question not Found")
    doc_ref.update({"assigned_to": a.reviewer_id, "status": "assigned"})
    return {"id": qid, "assigned_to": a.reviewer_id}


@app.post("/upload_file")
async def create_upload_file(file: UploadFile):
    bucket = storage.bucket()
    blob = bucket.blob(f"folder/{file.filename}")
    content = await file.read()
    blob.upload_from_string(content, content_type=file.content_type)  # type: ignore
    print("✅ File uploaded!")
    return {"filename": file.filename}
