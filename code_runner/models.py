from pydantic import BaseModel
from typing import Literal, Optional, Union, Any, Dict


class QuizData(BaseModel):
    params: Dict[str, Any]
    correct_answers: Dict[str, Any]
    intermediate: Optional[Dict[str, Any]] = None
    nDigits: int = 3
    sigfigs: int = 3


class CodeRunResponse(BaseModel):
    success: bool
    error: Optional[str] = None
    quiz_response: Optional[QuizData] = None
    http_status_code: Optional[int] = None
