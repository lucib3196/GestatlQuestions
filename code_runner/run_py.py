import importlib.util
import inspect
import types
from typing import Any

from pydantic import ValidationError
from starlette import status

from code_runner.models import CodeRunResponse, QuizData
from .utils import normalize_path


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


def run_generate_py(path: str, isTesting: bool = False) -> "CodeRunResponse":
    """
    Import a Python module from the given file path and run its `generate` function.
    When isTesting=True, call `generate(2)` and expect `result['test_results']['pass']`.
    Validate the final payload against QuizData.
    """
    # ---- Path validation ----
    try:
        p = normalize_path(path)
    except ValueError as e:
        return CodeRunResponse(
            success=False,
            error="No file argument provided for JavaScript execution.{e}",
            quiz_response=None,
            http_status_code=status.HTTP_400_BAD_REQUEST,
        )
    if not p.exists():
        return CodeRunResponse(
            success=False,
            error=f"File not found: {p}",
            quiz_response=None,
            http_status_code=status.HTTP_404_NOT_FOUND,
        )
    if not p.is_file():
        return CodeRunResponse(
            success=False,
            error=f"Path is not a regular file: {p}",
            quiz_response=None,
            http_status_code=status.HTTP_400_BAD_REQUEST,
        )
    if p.suffix.lower() != ".py":
        return CodeRunResponse(
            success=False,
            error=f"Unsupported file extension '{p.suffix}'. Expected .py.",
            quiz_response=None,
            http_status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )

    # ---- Import module ----
    try:
        module: types.ModuleType = import_module_from_path(str(p))
    except ImportError as e:
        return CodeRunResponse(
            success=False,
            error=f"Import error: {e}",
            quiz_response=None,
            http_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception as e:
        return CodeRunResponse(
            success=False,
            error=f"Unexpected error importing module: {e}",
            quiz_response=None,
            http_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # ---- Locate generate() ----
    generate = getattr(module, "generate", None)
    if not callable(generate):
        return CodeRunResponse(
            success=False,
            error="Function 'generate' not found or not callable in the Python module.",
            quiz_response=None,
            http_status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    # ---- Call generate() ----
    # Match JS behavior: when testing, pass 2; otherwise no arguments if possible.
    # If the signature requires an arg, pass 0 in non-testing mode.
    try:
        sig = inspect.signature(generate)
        if isTesting:
            args: tuple[Any, ...] = (2,) if len(sig.parameters) >= 1 else ()
        else:
            # Prefer zero args; if at least one required positional param exists, pass 0
            requires_positional = any(
                p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
                and p.default is p.empty
                for p in sig.parameters.values()
            )
            args = (0,) if requires_positional else ()
    except Exception:
        # If introspection fails, fall back to JS-like behavior
        args = (2,) if isTesting else ()

    try:
        result = generate(*args)
    except Exception as e:
        return CodeRunResponse(
            success=False,
            error=f"Error executing 'generate': {e}",
            quiz_response=None,
            http_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # ---- Test-mode semantics
    if isTesting:
        # Expect dict-like result with test_results.pass
        if not isinstance(result, dict):
            return CodeRunResponse(
                success=False,
                error="Test run expected a dict-like result with 'test_results', but got non-dict.",
                quiz_response=None,
                http_status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        test_results = result.get("test_results")
        if not isinstance(test_results, dict):
            return CodeRunResponse(
                success=False,
                error="Test run expected 'result.test_results' but it was missing or invalid.",
                quiz_response=None,
                http_status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        passed = test_results.get("pass")
        if passed not in (0, 1, True, False):
            return CodeRunResponse(
                success=False,
                error="'test_results.pass' must be 0/1 or boolean.",
                quiz_response=None,
                http_status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        if not bool(passed):
            msg = test_results.get("message", "Python test failed.")
            # Test executed successfully, but the test assertion failed.
            return CodeRunResponse(
                success=False,
                error=f"Test failed: {msg}",
                quiz_response=None,
                http_status_code=status.HTTP_200_OK,
            )

    # ---- Validate against QuizData ----
    try:
        quiz_data = QuizData(**result) if isinstance(result, dict) else QuizData.model_validate(result)  # type: ignore
    except ValidationError as ve:
        return CodeRunResponse(
            success=False,
            error=f"Output did not match expected QuizData schema: {ve}",
            quiz_response=None,
            http_status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    except Exception as e:
        return CodeRunResponse(
            success=False,
            error=f"Error constructing QuizData: {e}",
            quiz_response=None,
            http_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # ---- Success ----
    return CodeRunResponse(
        success=True,
        error=None,
        quiz_response=quiz_data,
        http_status_code=status.HTTP_200_OK,
    )


def test():
    path = r"code_runner\test.py"
    print(run_generate_py(path, isTesting=True))


if __name__ == "__main__":
    test()
