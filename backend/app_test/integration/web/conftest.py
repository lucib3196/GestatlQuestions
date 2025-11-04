from pathlib import Path
import pytest
from src.api.models import FileData


@pytest.fixture
def question_data():
    """Minimal question payload."""
    return {
        "title": "SomeTitle",
        "ai_generated": True,
        "isAdaptive": True,
        "createdBy": "John Doe",
        "user_id": 1,
    }


@pytest.fixture
def server_files():
    """Static assets used by question endpoints."""
    base = Path("app_test/test_assets/code")
    return [
        FileData(filename="server.js", content=(base / "generate.js").read_bytes()),
        FileData(filename="server.py", content=(base / "generate.py").read_bytes()),
    ]
