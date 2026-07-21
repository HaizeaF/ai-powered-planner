"""Shared state definition for the assistant's conversational graph."""
from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class GraphState(TypedDict):
    """State passed between nodes of the conversational graph."""
    messages: Annotated[list[BaseMessage], add_messages]
    tool_report: str