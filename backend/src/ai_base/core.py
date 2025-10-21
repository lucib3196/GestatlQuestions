from pydantic_settings import BaseSettings
from pydantic import BaseModel, Field
from typing import Optional


class AIModel(BaseModel):
    name: Optional[str] = None  # A name such as (fast, long context etc)
    provider: str = Field(..., description="e.g. Openai, gemini, claude etc")
    model: str = Field(..., description="e.g. gpt-4o-mini, claude 3 opus")
    api_key: Optional[str] = Field(None, description="API Key for this provider")
    base_url: Optional[str] = None  # optional custom endpoint


class AICoreSettings(BaseSettings):
    default_api_key: Optional[str] = Field(
        None, description="Fallback key if model missing"
    )
    fast_model: Optional[AIModel] = None
    base_model: AIModel
    long_context_model: Optional[AIModel] = None

    def get_api_key(self, model_name: str) -> str | None:
        model = getattr(self, model_name)
        return model.api_key or self.default_api_key

    class Config:
        env_file = ".env"
        env_prefix = "AI_"
