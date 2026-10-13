from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "development"
    log_level: str = "INFO"
    log_format: str = "console"

    database_url: str = "postgresql+psycopg://soccera:soccera@localhost:5432/soccera"
    database_pool_size: int = 10

    redis_url: str = "redis://localhost:6379/0"

    api_football_base_url: str = "https://v3.football.api-sports.io"
    api_football_key: str = ""
    api_football_rate_limit_per_minute: int = 10
    api_football_timeout_seconds: int = 15

    live_poll_interval_seconds: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
