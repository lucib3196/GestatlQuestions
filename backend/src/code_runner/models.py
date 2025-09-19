from pydantic import BaseModel
from typing import Literal, Optional, Union, Any, Dict, List


class QuizData(BaseModel):
    params: Dict[str, Any]
    correct_answers: Dict[str, Any]
    intermediate: Optional[Dict[str, Any]] = None
    test_results: Optional[Dict[str, Any]] = None
    logs: Optional[List[Any]] = []
    nDigits: Optional[int] = 3
    sigfigs: Optional[int] = 3


class CodeRunResponse(BaseModel):
    success: bool
    error: Optional[str] = None
    quiz_response: Optional[QuizData] = None
    http_status_code: Optional[int] = None



class CodeRunException(Exception):
    def __init__(self, *, error: str, http_status_code: int, quiz_response=None):
        self.response = CodeRunResponse(
            success=False,
            error=error,
            http_status_code=http_status_code,
            quiz_response=quiz_response,
        )
        super().__init__(error)