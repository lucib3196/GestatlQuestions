from typing import Any
import importlib.util
from code_runner.models import QuizData, CodeRunResponse
from pydantic import ValidationError


def import_module_from_path(path: str, module_name: str = "generate") -> Any:
    """
    Dynamically imports a Python module from a given file path.

    Args:
        path (str): Path to the Python module.
        module_name (str): Name to assign to the imported module.

    Returns:
        module: The imported module object.

    Raises:
        ImportError: If the module cannot be imported.
    """
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec from path: {path}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        raise ImportError(f"Error executing module '{path}': {e}")
    return module


def run_generate_py(path: str) -> CodeRunResponse:
    """
    Imports a Python module from the given path and runs its 'generate' function.
    Validates the output against the QuizData schema.

    Args:
        path (str): Path to the Python module.

    Returns:
        CodeRunResponse: Result of the code execution and validation.
    """
    try:
        module = import_module_from_path(path)
    except ImportError as e:
        return CodeRunResponse(
            success=False,
            error=str(e),
            quiz_response=None,
            http_status_code=500,
        )

    if not hasattr(module, "generate") or not callable(getattr(module, "generate")):
        return CodeRunResponse(
            success=False,
            error="Function 'generate' not found or not callable in the Python module.",
            quiz_response=None,
            http_status_code=500,
        )

    try:
        data = module.generate()
    except Exception as e:
        return CodeRunResponse(
            success=False,
            error=f"Error executing 'generate': {e}",
            quiz_response=None,
            http_status_code=500,
        )

    try:
        quiz_data = QuizData(**data)
    except ValidationError as ve:
        return CodeRunResponse(
            success=False,
            error=f"Output JSON did not match expected schema: {ve}",
            quiz_response=None,
            http_status_code=422,
        )

    return CodeRunResponse(
        success=True,
        error=None,
        quiz_response=quiz_data,
        http_status_code=200,
    )


def test():
    path = r"backend\processing\code_runners\test.py"
    print(run_generate_py(path))


if __name__ == "__main__":
    test()
