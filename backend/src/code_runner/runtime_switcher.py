from .run_js import execute_javascript as execute_js
from .run_py import run_generate_py as execute_py
from pathlib import Path
from typing import Literal, TypeAlias
from pydantic import BaseModel
from typing import Callable
from pydantic import BaseModel, Field
from .utils import validate_filepath
from .models import CodeRunException, CodeRunResponse
from src.api.core import logger

RunnerFunc: TypeAlias = Callable[[str, bool], CodeRunResponse]


class Generator(BaseModel):
    runner: RunnerFunc = Field(
        ..., description="Function that executes code for this runtime"
    )
    extensions: list[str] = Field(
        ..., description="Supported file extensions for this runtime"
    )


GENERATOR_MAPPING = {
    "python": Generator(runner=execute_py, extensions=[".py"]),
    "javascript": Generator(runner=execute_js, extensions=[".mjs", ".js"]),
}


def run_generate(
    path: str | Path,
    language: Literal["python", "javascript"],
    isTesting: bool = False,
):
    """Run code generation for a given language and path with logging."""
    path = Path(path)
    logger.debug(
        f"[Runtime Switcher] Starting execution | language={language} | path='{path}' | testing={isTesting}"
    )

    try:
        generator = GENERATOR_MAPPING[language]
        runner = generator.runner
        valid_extensions = generator.extensions

        logger.debug(
            f"[Runtime Switcher] Validating file path '{path}' with extensions {valid_extensions}"
        )
        validate_filepath(path, extensions=valid_extensions)

        # Normalize path just in case
        posix_path = path.as_posix()
        logger.info(
            f"[Runtime Switcher] Executing {language.upper()} runner on '{posix_path}'"
        )

        result = runner(posix_path, isTesting)
        logger.debug(
            f"[Runtime Switcher] Execution completed successfully for {language}"
        )
        return result

    except CodeRunException as e:
        logger.error(
            f"[Runtime Switcher] Known CodeRunException in {language} | {e}",
            exc_info=True,
        )
        raise

    except Exception as e:
        logger.exception(
            f"[Runtime Switcher] Unexpected error during {language} execution | path='{path}'"
        )
        raise CodeRunException(error=str(e), http_status_code=500)


# def run_generate(path: Union[str, Path], isTesting: bool = False) -> CodeRunResponse:
#     generator = {"server.js": execute_javascript, "server.py": run_generate_py}

#     # Check that the file exists
#     if not os.path.isfile(path):
#         return CodeRunResponse(
#             success=False,
#             error=f"File not Found: {path}",
#             quiz_response=None,
#             http_status_code=404,
#         )
#     base_name = os.path.basename(path)
#     try:
#         if base_name in generator:
#             result: CodeRunResponse = generator[base_name](str(path), isTesting)
#             return result
#         else:
#             return CodeRunResponse(
#                 success=False,
#                 error=f"Unsupported file: {base_name}",
#                 quiz_response=None,
#                 http_status_code=400,
#             )
#     except Exception as e:
#         return CodeRunResponse(
#             success=False,
#             error=f"Unexpected error occurred while running generate function: {e}",
#             quiz_response=None,
#             http_status_code=500,
#         )
