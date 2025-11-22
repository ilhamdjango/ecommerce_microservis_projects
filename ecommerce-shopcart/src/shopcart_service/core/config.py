import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # Database configuration - DOCKER-COMPOSE-DAKI POSTGRES_ DƏYİŞƏNLƏRİNİ OXU
    DB_HOST: str = os.getenv("POSTGRES_HOST", "db-shopcart")
    DB_USER: str = os.getenv("POSTGRES_USER", "shopcart_user")
    DB_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "12345")
    DB_NAME: str = os.getenv("POSTGRES_DB", "shopcart_db")
    DB_PORT: int = 5432
    
    # App configuration
    SECRET_KEY: str = "d4a18b05f4a744a6a2d9981c57cb07a635fe01912c994e5f68b4db7b6b6a7f2d"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DEBUG: bool = True
    PORT: int = 8000
    ENV: str = "production"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore"
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()