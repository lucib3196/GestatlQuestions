# Stdlib
import subprocess
from pathlib import Path
from typing import Union, Any

# Third-party
import execjs
import json5
from pydantic import ValidationError
from starlette import status

# Internal
from src.code_runner.models import CodeRunResponse, QuizData
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


def execute_javascript(
    path: Union[str, Path], isTesting: bool = False
) -> CodeRunResponse:
    # Normalize/validate path
    try:
        file_path = normalize_path(path)
    except ValueError as e:
        return CodeRunResponse(
            success=False,
            error=f"No file argument provided for JavaScript execution. {e}",
            quiz_response=None,
            http_status_code=status.HTTP_400_BAD_REQUEST,
        )

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

    # Read JS and wrap with logger + call shim
    try:
        user_js = file_path.read_text(encoding="utf-8")
        js_code = (
            """
            var logs = [];

            // capture console.log into logs array
            console.log = function(...args) {
            const processed = args.map(arg => {
                if (typeof arg === "object") {
                try {
                    return JSON.stringify(arg);
                } catch (e) {
                    return "[Unserializable Object]";
                }
                }
                return String(arg);
            });

            logs.push(processed.join(" "));
            };

            // `generate` should exist in user code.
            // We allow an optional arg; tests can pass a fixed value.
            """
            + user_js
            + """
            function callWithLogs(arg) {
            logs = [];  // reset
            let out = {};
            try {
                const safeArg = (arg && typeof arg === "object") ? arg : {};
                out = (typeof generate === "function") ? generate(safeArg) : undefined;
            } catch (e) {
                console.log("Error in generate:", e);
            }
            return { result: out, logs: logs };
            }
        """
        )
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

    # Compile JS
    try:
        ctx = execjs.compile(js_code)
    except execjs.RuntimeUnavailableError:
        return CodeRunResponse(
            success=False,
            error="No JavaScript runtime available. Install Node.js so execjs can use it.",
            quiz_response=None,
            http_status_code=status.HTTP_424_FAILED_DEPENDENCY,
        )
    except execjs.ProgramError as e:
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

    # Verify generate exists
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

    # Execute: tests pass a fixed arg (e.g., 2); normal run passes null
    try:
        raw = ctx.call("callWithLogs", 2 if isTesting else None)
        # raw should look like: { result: <payload>, logs: [...] }
        if not isinstance(raw, dict):
            return CodeRunResponse(
                success=False,
                error="JavaScript did not return an object. Expected { result, logs }.",
                quiz_response=None,
                http_status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
    except execjs.ProgramError as e:
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

    # ---------------------------
    # Parse the *actual* payload:
    #   raw = { result: <payload>, logs: [...] }
    # Some generators nest under `result.results`, so handle both.
    # ---------------------------
    js_result: Any = raw.get("result", None)

    if js_result is None:
        return CodeRunResponse(
            success=False,
            error="Missing `result` in JavaScript return object.",
            quiz_response=None,
            http_status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    # If payload is nested like { result: { results: {...}, test_results: {...} } }
    logs = raw.get("logs", [])
    payload = (
        js_result.get("results", js_result)
        if isinstance(js_result, dict)
        else js_result
    )
    # Merge results + logs into one dict
    if isinstance(payload, dict):
        payload = {**payload, **{"logs": logs}}

    # If running tests, validate `test_results` if present
    if isTesting:
        test_meta = (
            js_result.get("test_results") if isinstance(js_result, dict) else None
        )
        if test_meta is not None:
            if not isinstance(test_meta, dict):
                return CodeRunResponse(
                    success=False,
                    error="Test run expected `result.test_results` as a dict.",
                    quiz_response=None,
                    http_status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )
            passed = test_meta.get("pass")
            if passed not in (0, 1, True, False):
                return CodeRunResponse(
                    success=False,
                    error="`test_results.pass` must be 0/1 or boolean.",
                    quiz_response=None,
                    http_status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )
            if not bool(passed):
                msg = test_meta.get("message", "JavaScript test failed.")
                return CodeRunResponse(
                    success=False,
                    error=f"Test failed: {msg}",
                    quiz_response=None,
                    http_status_code=status.HTTP_200_OK,
                )

    # Validate against QuizData
    try:
        quiz_data = (
            QuizData(**payload)
            if isinstance(payload, dict)
            else QuizData.model_validate(payload)
        )
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
