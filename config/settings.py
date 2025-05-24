import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str
    redis_url: str = "redis://localhost:6379"
    environment: str = "development"
    
    class Config:
        env_file = ".env"

settings = Settings()
