#config
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # Database configuration
    DB_HOST: str = "db-wishlist"
    DB_USER: str = "wishlist_user"
    DB_PASSWORD: str = "12345"
    DB_NAME: str = "wishlist_db"
    DB_PORT: int = 5432
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # App configuration
    SECRET_KEY: str = "d4a18b05f4a744a6a2d9981c57cb07a635fe01912c994e5f68b4db7b6b6a7f2d"
    DEBUG: bool = True
    PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()