from pathlib import Path
from backend_api.model.questions_models import QuestionMetaNew
from backend_api.model.questions_models import Question
from backend_api.data.database import SessionDep
import json

qmeta_path = Path(r"local_questions\DistanceTraveledByCar\qmeta.json")
qmeta_data = QuestionMetaNew(**json.loads(qmeta_path.read_text(encoding="utf-8")))


question = Question(
    qtype=qmeta_data.qtype,
    title=qmeta_data.title,
    isAdaptive=qmeta_data.isAdaptive,
    createdBy="lberm007@ucr.edu",
    language=qmeta_data.language,
    ai_generated=qmeta_data.ai_generated,
)
