from typing import List
from fastapi import APIRouter, Depends
from fastapi import UploadFile
from api.service import file_management as file_service

router = APIRouter(prefix="/file")


@router.post("/upload_files")
async def upload_file(files: List[UploadFile]):
    return await file_service.upload_files(files)


@router.post("/upload_folder")
async def upload_folder(files: List[UploadFile]):
    return await file_service.upload_folder(files)
