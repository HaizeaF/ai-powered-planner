"""Centralized configuration for the backend."""
import os
from dotenv import load_dotenv
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH)

class Config:
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    # Database
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR / 'db' / 'planner.db'}"
    CHECKPOINT_DB_PATH: str = str(BASE_DIR / "db" / "checkpoints.db")

    # LLM
    LLM_MODEL: str = "qwen3:14b"
    CHAT_TIMEOUT_SECONDS: int = 120

    # CORS
    CORS_ORIGINS: list[str] = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "").split(",")]