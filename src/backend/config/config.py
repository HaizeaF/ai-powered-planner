"""Centralized configuration for the backend."""

from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Config:
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    GRAPH_IMAGE_PATH: str = str(BASE_DIR / "graph" / "graph.png")
    
    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'db' / 'planner.db'}"

    # LLM
    LLM_MODEL: str = "llama3"