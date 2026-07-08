"""SQLite database configuration and session management."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from src.backend.config.config import Config

engine = create_async_engine(Config.DATABASE_URL, echo=True)

async def init_db() -> None:
    """Create the tables if they do not exist."""
    Config.BASE_DIR.joinpath("db").mkdir(parents=True, exist_ok=True)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session."""
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session