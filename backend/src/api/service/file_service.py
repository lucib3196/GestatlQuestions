# --- Standard Library ---
import io
import json
import shutil
import zipfile
import asyncio
from pathlib import Path
from typing import List, Optional, Union, Sequence

# --- Third-Party ---
from fastapi import UploadFile, HTTPException
from starlette import status

# --- Internal ---
from src.api.response_models import SuccessfulResponse


# Donwload Utilits
import io, zipfile

# Configuration for file size and filetypes
MAX_FILE_SIZE_MB = 5
ALLOWED_EXTENSIONS = {
    # Images
    ".png",
    ".jpg",
    ".jpeg",
    # Documents
    ".pdf",
    ".txt",
    ".html",
    ".json",
    # Code
    ".py",
    ".js",
    ".bin",
}
ALLOWED_MIME_TYPES = {
    "image/png",
    "image/jpeg",
    "application/pdf",
    "text/plain",
    "text/html",
    "application/json",
    "text/x-python",
    "application/javascript",
    "application/octet-stream",
    "text/javascript",
}
ALLOWED_ZIP_EXTENSIONS = {"application/zip", "application/x-zip-compressed"}


class SuccessFileServiceResponse(SuccessfulResponse):
    path: str | Path


class FileService:
    def __init__(self, base_path: Path | str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def validate_file(self, file: UploadFile) -> UploadFile:
        if not file.filename:
            raise HTTPException(status_code=400, detail="There is no file")

        file = await self.validate_file_size(file)
        return file

    async def save_file(self, file: UploadFile, destination: str) -> Path:
        await self.validate_file(file)
        dest_path = self.base_path / destination
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return dest_path

    async def convert_to_uploadfile(
        self, path: Union[Path, str, UploadFile]
    ) -> UploadFile:
        if isinstance(path, UploadFile):
            return path
        path = Path(path)
        upload_file = UploadFile(
            filename=path.name,
            file=open(path, "rb"),  # important: open in binary mode
        )
        await self.validate_file(upload_file)
        return upload_file

    async def save_files(
        self, files: List[UploadFile], destination: str
    ) -> SuccessFileServiceResponse:
        try:
            await asyncio.gather(*[self.save_file(f, destination) for f in files])
            return SuccessFileServiceResponse(
                status=status.HTTP_200_OK,
                detail="Saved files succesfully",
                path=self.base_path / destination,
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Could not process file uploads {str(e)}",
            )

    async def download_zip(
        self,
        files: Sequence[Union[Path, str, UploadFile]],
        folder_name: Optional[str],
    ) -> bytes:
        """Bundle multiple files into a zip and return as StreamingResponse."""
        upload_files: List[UploadFile] = await asyncio.gather(
            *(self.convert_to_uploadfile(f) for f in files)
        )

        buffer = io.BytesIO()
        manifest: list[dict] = []
        folder_name = folder_name or "Untitled_Content"

        zip_path = self.base_path / f"{folder_name}.zip"

        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
            for f in upload_files:
                fname = f.filename or "UntitledFile.txt"
                arcname = f"{folder_name}/{fname}"
                data = await f.read()
                z.writestr(arcname, data)
                manifest.append({"file": arcname, "size": len(data)})

            z.writestr(
                "MANIFEST.json",
                json.dumps(
                    {"count": len(manifest), "files": manifest},
                    ensure_ascii=False,
                    indent=2,
                ),
            )
        buffer.seek(0)
        return buffer.getvalue()  # type: bytes

    # Helpers
    async def validate_file_size(self, file: UploadFile) -> UploadFile:
        try:
            contents = await file.read()
            if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
                raise HTTPException(
                    status_code=400,
                    detail=f"{file.filename} exceeds {MAX_FILE_SIZE_MB}MB",
                )
            await file.seek(0)
            return file
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not read file contents {str(e)}",
            )

    async def validate_file_contents(self, file: UploadFile) -> bool:
        try:
            assert file.filename
            if not file.content_type:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail="Cannot determine the file's content type",
                )

            if file.content_type.lower() not in ALLOWED_MIME_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f"File of Content type {file.content_type} is not allowed",
                )
            ext = Path(file.filename).suffix.lower()

            if ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400, detail=f"Invalid file extension: {ext}"
                )
            return True
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not validate file contents {str(e)}",
            )


CONTENT_TYPE_MAPPING = {
    # Text
    ".txt": "text/plain",
    ".csv": "text/csv",
    ".json": "application/json",
    ".xml": "application/xml",
    # Web
    ".html": "text/html",
    ".htm": "text/html",
    ".css": "text/css",
    ".js": "application/javascript",
    ".ts": "application/typescript",
    ".jsx": "text/jsx",
    ".tsx": "text/tsx",
    # Images
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".ico": "image/vnd.microsoft.icon",
    ".webp": "image/webp",
    # Documents
    ".pdf": "application/pdf",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".ppt": "application/vnd.ms-powerpoint",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    # Code
    ".py": "text/x-python",
    ".java": "text/x-java-source",
    ".c": "text/x-c",
    ".cpp": "text/x-c++",
    ".h": "text/x-c",
    ".hpp": "text/x-c++",
    # Compressed
    ".zip": "application/zip",
    ".tar": "application/x-tar",
    ".gz": "application/gzip",
    ".rar": "application/vnd.rar",
    ".7z": "application/x-7z-compressed",
}


def get_content_type(filename: str) -> str:
    """Return MIME type based on file extension, defaults to octet-stream."""
    import os

    ext = os.path.splitext(filename)[1].lower()
    return CONTENT_TYPE_MAPPING.get(ext, "application/octet-stream")
