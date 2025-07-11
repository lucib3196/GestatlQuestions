import logging
from fastapi import FastAPI, HTTPException, UploadFile
from pydantic import BaseModel
import uuid
from typing import Annotated
from .config import db
from firebase_admin import storage

from backend_api.web.authentication import router
from backend_api.web.file_management import router as file_router
from backend_api.web.local_questions import router as local_question_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


app = FastAPI()
app.include_router(router)
app.include_router(file_router)
app.include_router(local_question_router)


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
    blob.upload_from_string(content, content_type=file.content_type)
    print("✅ File uploaded!")
    return {"filename": file.filename}
