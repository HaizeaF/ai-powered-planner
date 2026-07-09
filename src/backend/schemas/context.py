"""Shared context passed to the agent."""
from dataclasses import dataclass
from sqlmodel.ext.asyncio.session import AsyncSession

@dataclass
class Context:
    """Runtime context available to agent tools."""
    session: AsyncSession