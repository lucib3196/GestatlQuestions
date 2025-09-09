from .run_js import run_js, execute_javascript
from .run_py import run_generate_py
from src.code_runner.models import CodeRunResponse
import os
from pathlib import Path
from typing import Union


def run_generate(path: Union[str, Path], isTesting: bool = False) -> CodeRunResponse:
    generator = {"server.js": execute_javascript, "server.py": run_generate_py}

    # Check that the file exists
    if not os.path.isfile(path):
        return CodeRunResponse(
            success=False,
            error=f"File not Found: {path}",
            quiz_response=None,
            http_status_code=404,
        )
    base_name = os.path.basename(path)
    try:
        if base_name in generator:
            result: CodeRunResponse = generator[base_name](str(path), isTesting)
            return result
        else:
            return CodeRunResponse(
                success=False,
                error=f"Unsupported file: {base_name}",
                quiz_response=None,
                http_status_code=400,
            )
    except Exception as e:
        return CodeRunResponse(
            success=False,
            error=f"Unexpected error occurred while running generate function: {e}",
            quiz_response=None,
            http_status_code=500,
        )


if __name__ == "__main__":
    js_path = r"backend/processing/code_runners/test.js"
    py_path = r"backend/processing/code_runners/test.py"

    try:
        print("JS Output:")
        print(run_js(js_path))
    except Exception as e:
        print(f"JS Error: {e}")

    try:
        print("\nPython Output:")
        print(run_generate_py(py_path))
    except Exception as e:
        print(f"Python Error: {e}")
