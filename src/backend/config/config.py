"""Centralized configuration for the backend."""

from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Config:
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    GRAPH_IMAGE_PATH: str = str(BASE_DIR / "graph" / "graph.png")
    
    # Database
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR / 'db' / 'planner.db'}"
    CHECKPOINT_DB_PATH: str = str(BASE_DIR / "db" / "checkpoints.db")

    # LLM
    LLM_MODEL: str = "qwen3:8b"

    # CORS
    CORS_ORIGINS: str = ""