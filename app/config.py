# app/config.py
from pydantic import BaseModel
from functools import lru_cache
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

class Settings(BaseModel):
    PROJECT_NAME: str = "Auth Service"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Required settings with default values from environment variables
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:tapan@123@localhost/auth_db"
    )
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "default-secret-key-change-this-in-production"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "180"))

@lru_cache()
def get_settings() -> Settings:
    return Settings()