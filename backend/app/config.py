from pydantic_settings import BaseSettings
from pydantic import ConfigDict
import os

class Settings(BaseSettings):
    model_config = ConfigDict(env_file="../.env", extra="ignore")

    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    DATABASE_URL: str = "sqlite+aiosqlite:///./crm_local.db"
    REDIS_URL: str = "redis://redis:6379"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    STREAM_SPEED: int = 1
    LOG_LEVEL: str = "INFO"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENV: str = "local"  # local, docker, production

settings = Settings()
