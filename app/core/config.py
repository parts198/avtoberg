from functools import lru_cache
from pydantic import BaseSettings, AnyHttpUrl
from typing import List, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Ozon Multi-Store SaaS"
    API_V1_STR: str = "/api"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    REDIS_URL: str = "redis://localhost:6379/0"
    OZON_RATE_LIMIT_PER_MINUTE: int = 90
    OZON_STOCK_UPDATE_COOLDOWN_SECONDS: int = 30
    LOG_LEVEL: str = "INFO"
    ALLOWED_HOSTS: List[str] = []
    BACKOFF_MAX_RETRIES: int = 5
    BACKOFF_BASE: float = 0.5
    OZON_API_URL: AnyHttpUrl = "https://api-seller.ozon.ru"

    class Config:
        case_sensitive = True
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
