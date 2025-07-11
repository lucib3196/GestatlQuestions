from typing import List
from fastapi import APIRouter, Depends
from fastapi import UploadFile
from backend_api.service import file_management as file_service

router = APIRouter(prefix="/file")


@router.post("/upload_file")
async def upload_file(file: UploadFile):
    return await file_service.upload_file(file)


@router.post("/upload_folder")
async def upload_folder(files: List[UploadFile]):
    return await file_service.upload_folder(files)
