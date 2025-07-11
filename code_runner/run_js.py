import subprocess
from pathlib import Path
import json5
from pydantic import ValidationError
from code_runner.models import CodeRunResponse, QuizData


def run_js(path: str) -> CodeRunResponse:
    """
    Runs a JavaScript file using Node.js and parses its output as JSON.
    Expects the JS file to output a JSON object via console.log(generate()).
    """
    js_path = str(Path(path))  # Ensure cross-platform path handling

    try:
        result = subprocess.run(
            ["node", js_path, "generate"],
            capture_output=True,
            text=True,
            timeout=5,
        )
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


def test():
    path = Path("local_questions/BendingStressInSimplySupportedBeam/server.js")
    print(run_js(str(path)))


if __name__ == "__main__":
    test()