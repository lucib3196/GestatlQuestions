from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class LLMConfiguration(BaseSettings):
    """Configuration for LLM model and data paths."""

    # -------------------------------------------------------------------------
    # Model Settings
    # -------------------------------------------------------------------------
    fast_model: str = "gpt-5-nano"
    base_model: str = "gpt-4o-mini"
    long_context_model: str = "gpt-5"
    model_provider: str = "openai"
    embedding_model: str = "text-embedding-3-large"
    n_search_queries: int = 3

    # -------------------------------------------------------------------------
    # Storage Paths
    # -------------------------------------------------------------------------
    vector_store_path: Path = Path("src/ai_workspace/vectorstores/QUESTIONMOD_VS").resolve()
    ROOT_DIR: Path = Path(__file__).resolve().parents[2]
    question_csv_path: Path = (ROOT_DIR / "data" / "QuestionDataV2_06122025_classified.csv").resolve()

    # -------------------------------------------------------------------------
    # Model Config
    # -------------------------------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
    )

    # -------------------------------------------------------------------------
    # Hash Support
    # -------------------------------------------------------------------------
    def __hash__(self) -> int:
        return hash(
            (
                self.fast_model,
                self.base_model,
                self.long_context_model,
                self.model_provider,
                self.embedding_model,
                self.n_search_queries,
                str(self.vector_store_path),
                str(self.question_csv_path),
            )
        )
