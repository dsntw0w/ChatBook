# backend/app/config.py
import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# config.py 기준으로 프로젝트 루트(.env 위치) 계산
# config.py → app → backend → chatbook/
_BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.environ.get("ENV_FILE", str(_BASE_DIR / ".env")),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = "sqlite:///app/data/chatbook.db"

    # API Keys
    OPENAI_API_KEY: str = "sk-dummy"
    GEMINI_API_KEY: str = "gemini-dummy"
    DEEPSEEK_API_KEY: str = "deepseek-dummy"
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"

    # Demo Mode
    USE_DEMO_MODE: bool = True

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"


settings = Settings()
