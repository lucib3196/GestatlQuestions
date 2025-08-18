import subprocess
from pathlib import Path
import json5
from pydantic import ValidationError
from code_runner.models import CodeRunResponse, QuizData
from starlette import status
from .utils import normalize_path


def run_js(path: str) -> CodeRunResponse:
    """
    Runs a JavaScript file using Node.js and parses its output as JSON.
    Expects the JS file to output a JSON object via console.log(generate()).
    """
    js_path = str(Path(path))  # Ensure cross-platform path handling

    try:
        result = subprocess.run(
            ["node", js_path, "generate()"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        print("This is the result")
    except subprocess.TimeoutExpired:
        return CodeRunResponse(
            success=False,
            error="JavaScript execution timed out.",
            quiz_response=None,
            http_status_code=504,
        )
    except Exception as e:
        return CodeRunResponse(
            success=False,
            error=f"Failed to execute JavaScript file '{js_path}': {e}",
            quiz_response=None,
            http_status_code=500,
        )

    stdout = result.stdout.strip()
    stderr = result.stderr.strip()

    if result.returncode != 0:
        return CodeRunResponse(
            success=False,
            error=f"JavaScript script returned an error:\n{stderr or stdout}",
            quiz_response=None,
            http_status_code=500,
        )

    if not stdout:
        return CodeRunResponse(
            success=False,
            error="No output was returned from the JavaScript script. Hint: There must be a console.log(generate())",
            quiz_response=None,
            http_status_code=500,
        )

    try:
        parsed = json5.loads(stdout)

    except Exception as e:
        return CodeRunResponse(
            success=False,
            error=f"Failed to parse output as JSON: {e}\nOutput was:\n{stdout}",
            quiz_response=None,
            http_status_code=400,
        )

    if not isinstance(parsed, dict):
        return CodeRunResponse(
            success=False,
            error="Output is not a JSON object (dict).",
            quiz_response=None,
            http_status_code=400,
        )

    try:
        quiz_data = QuizData(**parsed)
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
        http_status_code=200,
        quiz_response=quiz_data,
    )


from pathlib import Path
from typing import Union
import execjs


def execute_javascript(path: Union[str, Path], isTesting: bool = False):
    # Handle Case where file is Empty
    try:
        file_path = normalize_path(path)
    except ValueError as e:
        return CodeRunResponse(
            success=False,
            error="No file argument provided for JavaScript execution.{e}",
            quiz_response=None,
            http_status_code=status.HTTP_400_BAD_REQUEST,
        )

    # File Validation
    if not file_path.exists():
        return CodeRunResponse(
            success=False,
            error=f"File not found: {file_path}",
            quiz_response=None,
            http_status_code=status.HTTP_404_NOT_FOUND,
        )
    if not file_path.is_file():
        return CodeRunResponse(
            success=False,
            error=f"Path is not a regular file: {file_path}",
            quiz_response=None,
            http_status_code=status.HTTP_400_BAD_REQUEST,
        )
    if file_path.suffix.lower() not in {".js", ".mjs"}:
        return CodeRunResponse(
            success=False,
            error=f"Unsupported file extension '{file_path.suffix}'. Expected .js or .mjs.",
            quiz_response=None,
            http_status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )

    # try to Read Text
    try:
        js_code = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return CodeRunResponse(
            success=False,
            error="File is not valid UTF-8 text.",
            quiz_response=None,
            http_status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )
    except OSError as e:
        return CodeRunResponse(
            success=False,
            error=f"Failed to read file: {e}",
            quiz_response=None,
            http_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    try:
        ctx = execjs.compile(js_code)
    except execjs.RuntimeUnavailableError:
        return CodeRunResponse(
            success=False,
            error="No JavaScript runtime available. Install Node.js (e.g., https://nodejs.org) so execjs can use it.",
            quiz_response=None,
            http_status_code=status.HTTP_424_FAILED_DEPENDENCY,
        )
    except execjs.ProgramError as e:
        # JS syntax error or similar at compile time
        return CodeRunResponse(
            success=False,
            error=f"JavaScript compile error: {e}",
            quiz_response=None,
            http_status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    except Exception as e:
        return CodeRunResponse(
            success=False,
            error=f"Unexpected error compiling JavaScript: {e}",
            quiz_response=None,
            http_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Verify that generate function is valid
    try:
        has_generate = ctx.eval("typeof generate === 'function'")
        if not has_generate:
            return CodeRunResponse(
                success=False,
                error="The JavaScript file does not define a function named `generate`.",
                quiz_response=None,
                http_status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
    except execjs.ProgramError as e:
        return CodeRunResponse(
            success=False,
            error=f"Error checking for `generate` function: {e}",
            quiz_response=None,
            http_status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    # Execute the code
    try:
        result = ctx.call("generate", 2) if isTesting else ctx.call("generate")
    except execjs.ProgramError as e:
        # Runtime error inside JS (thrown exception)
        return CodeRunResponse(
            success=False,
            error=f"JavaScript runtime error: {e}",
            quiz_response=None,
            http_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception as e:
        return CodeRunResponse(
            success=False,
            error=f"Unexpected error during JS execution: {e}",
            quiz_response=None,
            http_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Check if testing and get the result
    if isTesting:
        # Expect the JS to return: { ..., test_results: { pass: 0|1, message: str } }
        test_results = (result or {}).get("test_results")
        if not isinstance(test_results, dict):
            return CodeRunResponse(
                success=False,
                error="Test run expected `result.test_results` but it was missing or invalid.",
                quiz_response=None,
                http_status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        passed = test_results.get("pass")
        if passed not in (0, 1, True, False):
            return CodeRunResponse(
                success=False,
                error="`test_results.pass` must be 0/1 or boolean.",
                quiz_response=None,
                http_status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        if not bool(passed):
            # Include any message if present for easier debugging
            msg = test_results.get("message", "JavaScript test failed.")
            return CodeRunResponse(
                success=False,
                error=f"Test failed: {msg}",
                quiz_response=None,
                http_status_code=status.HTTP_200_OK,  # test ran successfully but failed assertions
            )

    try:
        quiz_data = QuizData(**result)
    except ValidationError as e:
        return CodeRunResponse(
            success=False,
            error=f"Result did not match QuizData schema: {e}",
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

    return CodeRunResponse(
        success=True,
        error=None,
        quiz_response=quiz_data,
        http_status_code=status.HTTP_200_OK,
    )


def test():
    path = Path(r"code_runner\test2.js")

    print(execute_javascript(path, True))


if __name__ == "__main__":
    test()
