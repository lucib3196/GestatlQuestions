from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class LLMConfiguration(BaseSettings):
    fast_model: str = "gpt-5-nano"
    base_model: str = "gpt-5-mini"
    long_context_model: str = "gpt-5"
    model_provider: str = "openai"
    embedding_model: str = "text-embedding-3-large"
    n_search_queries: int = 3

    question_vs: Path = Path("ai_workspace/vectorstores/QUESTIONMOD_VS")
    question_csv_path: Path = Path("data/QuestionDataV2_06122025_classified.csv")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
    )
