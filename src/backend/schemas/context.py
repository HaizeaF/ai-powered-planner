"""Shared context passed to the agent."""
import asyncio
from dataclasses import dataclass, field
from sqlmodel.ext.asyncio.session import AsyncSession

@dataclass
class Context:
    """Runtime context available to agent tools."""
    session: AsyncSession
    session_lock: asyncio.Lock = field(default_factory=asyncio.Lock)