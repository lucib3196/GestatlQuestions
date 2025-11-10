from pathlib import Path
from typing import List

import fitz  # PyMuPDF


def pdf_page_to_image_bytes(pdf_path: str | Path, zoom: float = 2.0) -> List[bytes]:
    doc = fitz.open(pdf_path)
    image_bytes: List[bytes] = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        matrix = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=matrix)  # type: ignore
        image_bytes.append(pix.tobytes("png"))
    doc.close()
    return image_bytes
