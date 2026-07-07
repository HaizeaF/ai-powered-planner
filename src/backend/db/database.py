"""SQLite database configuration and session management."""

from typing import Generator
from sqlmodel import Session, SQLModel, create_engine
from src.backend.config.config import Config
from src.backend.models import task, project

engine = create_engine(Config.DATABASE_URL, echo=True, connect_args={"check_same_thread": False})

def init_db() -> None:
    """Create the tables if they do not exist."""
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session."""
    with Session(engine) as session:
        yield session