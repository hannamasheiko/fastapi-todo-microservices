from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Configuration for AI service."""

    openai_api_key: str = ""
    openai_model: str = "gpt-5-nano"

    ai_service_name: str = "ai_service"
    ai_service_host: str = "127.0.0.1"
    ai_service_port: int = 8003
    debug: bool = False

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        extra="ignore",
    )


settings = Settings()