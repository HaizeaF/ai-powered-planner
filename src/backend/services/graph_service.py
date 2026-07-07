"""Graph construction for the chatbot.

Builds a LangGraph StateGraph that wires together the rewriting, routing, retrieval, generation and grading nodes.
"""

from langgraph.graph import END, StateGraph
from src.backend.schemas.state import GraphState
from src.backend.graph.nodes import generate

def build_graph():
    """Build and compile the conversational graph for the chatbot."""
    graph = StateGraph(GraphState)

    graph.add_node("generate", generate)

    graph.set_entry_point("generate")
    graph.add_edge("generate", END)

    return graph.compile()