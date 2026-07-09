"""LLM definitions for the chatbot's agent."""

from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langgraph.checkpoint.base import BaseCheckpointSaver
from src.backend.chatbot.prompts_builder import answer_builder
from src.backend.config.config import Config
from src.backend.tools.project_tools import PROJECT_TOOLS
from src.backend.tools.task_tools import TASK_TOOLS
from src.backend.schemas.context import Context

_llm = ChatOllama(model=Config.LLM_MODEL, temperature=0)

def create_answer_agent(checkpointer: BaseCheckpointSaver):
    """Build the chatbot agent with the given checkpointer for cross-turn memory."""
    return create_agent(
        model=_llm,
        tools=[*PROJECT_TOOLS, *TASK_TOOLS],
        context_schema=Context,
        system_prompt=answer_builder(),
        checkpointer=checkpointer,
    )
