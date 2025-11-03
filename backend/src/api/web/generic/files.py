from __future__ import annotations

# --- Standard Library ---
from fastapi.routing import APIRouter
from fastapi.responses import StreamingResponse
from io import BytesIO

import asyncio
from pathlib import Path
# --- Third-Party ---
from fastapi import APIRouter
from pathlib import Path
from fastapi.responses import StreamingResponse
# --- Internal ---
import asyncio


router = APIRouter(prefix="/generic", tags=["files", "testing"])

test_image = Path(r"app_test/test_assets/images/test_image.png")

@router.post("/get_image")
async def preview_image(time_out: int = 0):
    image_bytes = test_image.read_bytes()
    await asyncio.sleep(time_out)
    return StreamingResponse(BytesIO(image_bytes), media_type="image/png")