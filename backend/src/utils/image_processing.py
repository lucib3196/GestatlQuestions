import base64
from pathlib import Path
from typing import Optional, Any
from langgraph.graph.state import CompiledStateGraph


def encode_image(image_path: str | Path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def handle_image_data(data) -> bytes:
    try:
        if isinstance(data, list):
            image_data = data[0]
            return base64.b64decode(image_data)
        else:
            raise NotImplemented
    except Exception as e:
        raise e


def write_image_data(
    image_bytes: bytes, folder_path: str | Path, filename: Optional[str] = None
) -> bool:
    try:
        path = Path(folder_path).resolve()
        if filename:
            path = path / filename
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

        if path.suffix != ".png":
            raise ValueError(
                "Suffix allowed is only PNG either missing or nnot allowed"
            )
        with open(path, "wb") as f:
            f.write(image_bytes)
        return True
    except Exception as e:
        raise Exception(f"Could not save image {str(e)}")


def save_graph_visualization(
    graph: CompiledStateGraph | Any,
    folder_path: str | Path,
    filename: Optional[str] = None,
):
    try:
        path = Path(folder_path).resolve()
        if filename:
            path = path / filename

        image_bytes = graph.get_graph().draw_mermaid_png()
        write_image_data(image_bytes, path)
        print(f"✅ Saved graph visualization at: {path}")
    except Exception as error:
        print(f"❌ Graph visualization failed: {error}")
