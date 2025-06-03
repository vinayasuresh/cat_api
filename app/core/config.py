from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "CAT API"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: str
    POSTGRES_DB: str
    
    DATABASE_URL: Optional[str] = None
    
    # JWT Settings
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Alert Monitoring Settings
    ALERT_FETCH_INTERVAL_SECONDS: int = 300  # Default to 5 minutes
    
    @property
    def sync_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"


class DevSettings(Settings):
    class Config:
        env_file = ".env.dev"


class ProdSettings(Settings):
    class Config:
        env_file = ".env.prod"


@lru_cache()
def get_settings():
    env = os.getenv("APP_ENV", "dev").lower()
    if env == "prod":
        return ProdSettings()
    return DevSettings()


settings = get_settings()
