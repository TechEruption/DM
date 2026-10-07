from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = (
        "postgresql+psycopg://postgres:YOUR_DATABASE_PASSWORD"
        "@db.jzuqjibyqpcoxjmyuqoe.supabase.co:5432/postgres?sslmode=require"
    )
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    app_env: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
DATABASE_URL = settings.database_url
APP_ENV = settings.app_env
