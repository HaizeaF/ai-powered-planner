"""SQLite database configuration and session management."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from src.backend.config.config import Config

engine = create_async_engine(Config.DATABASE_URL, echo=True)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session.
    
    This is the transaction boundary: everything done with this session during the request is committed together at the end. If anything raises, the whole transaction is rolled back, nothing partially done gets persisted.
    """
    async with AsyncSession(engine, expire_on_commit=False) as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise