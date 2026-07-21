"""Prompt builders for every prompt used across the app."""
from datetime import datetime, timezone
from src.backend.prompts.prompts import ANSWER_PROMPT, TOOL_PROMPT
from typing import Any

def _shared_context(now: datetime | None = None) -> dict[str, str]:
    """Runtime values common to every prompt in this module."""
    current = now or datetime.now(timezone.utc)

    return {"current_date": current.strftime("%Y-%m-%d")}

def tool_agent_builder(now: datetime | None = None, **overrides: Any) -> str:
    """Render the system prompt used by the internal tool-selection agent."""
    context = {**_shared_context(now), **overrides}

    return TOOL_PROMPT.format(**context)

def answer_agent_builder(now: datetime | None = None, **overrides: Any) -> str:
    """Render the system prompt used by the user-facing answer agent."""
    context = {**_shared_context(now), **overrides}

    return ANSWER_PROMPT.format(**context)