from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    """Конфігурація додатку"""

    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://todo_user:password123@localhost:5432/todo_db"
    )

    # JWT
    secret_key: str = os.getenv(
        "SECRET_KEY",
        "your-secret-key-min-32-chars"
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15

    # API
    api_host: str = os.getenv("API_HOST", "127.0.0.1")
    api_port: int = int(os.getenv("API_PORT", 8000))
    debug: bool = os.getenv("DEBUG", "True") == "True"

    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", 6379))
    redis_db: int = int(os.getenv("REDIS_DB", 0))
    cache_ttl: int = 300  # 5 хвилин


    class Config:
        env_file = ".env"


settings = Settings()