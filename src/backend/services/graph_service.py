"""Graph construction for the chatbot."""
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, StateGraph
from src.backend.chatbot.nodes import run_tool_agent, run_answer_agent
from src.backend.schemas.context import Context
from src.backend.schemas.state import GraphState

def build_graph(checkpointer: BaseCheckpointSaver):
    """Build and compile the conversational graph for the chatbot."""
    graph = StateGraph(GraphState, context_schema=Context)

    graph.add_node("tool_agent", run_tool_agent)
    graph.add_node("answer_agent", run_answer_agent)

    graph.set_entry_point("tool_agent")

    graph.add_edge("tool_agent", "answer_agent")
    graph.add_edge("answer_agent", END)

    return graph.compile(checkpointer=checkpointer)
