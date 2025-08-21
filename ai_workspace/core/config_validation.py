from pathlib import Path
from ai_workspace.core import LLMConfiguration
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from pathlib import Path
from .config import LLMConfiguration

def load_vectorstore(path: Path, embeddings: OpenAIEmbeddings) -> FAISS:
    from langchain_community.vectorstores import FAISS

    return FAISS.load_local(
        str(path),
        embeddings,
        allow_dangerous_deserialization=True,
    )


class InitError(RuntimeError):
    pass


def validate_paths(cfg: "LLMConfiguration") -> None:
    print(cfg.question_vs)
    vs_path = cfg.question_vs
    csv_path = cfg.question_csv_path
    if isinstance(cfg.question_vs, str):
        vs_path = Path(vs_path)
    if isinstance(cfg.question_csv_path, str):
        csv_path = Path(csv_path)

    if not vs_path.exists():
        raise InitError(f"Vectorstore path does not exist: {vs_path}")
    if csv_path.suffix.lower() != ".csv" or not csv_path.exists():
        raise InitError(f"Question CSV not found: {csv_path}")