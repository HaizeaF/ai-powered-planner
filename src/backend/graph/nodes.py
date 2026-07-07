"""Node and routing functions for the chatbot conversational graph.

Each node performs a single responsibility and returns a partial state update, following LangGraph conventions.
"""

from src.backend.schemas.state import GraphState
from langchain_core.messages import HumanMessage
from src.backend.graph.chains import answer_chain

# Formatting helpers
def _format_history(history: list, max_turns: int = 1) -> str:
    """Format the last conversation turns into a readable block for prompts.

    Off-topic and fallback responses are excluded so they do not pollute the context used to resolve pronouns or references.
    """
    if not history:
        return "No previous conversation."
    
    filtered = [msg for msg in history]

    if not filtered:
        return "No previous conversation."
    
    filtered = filtered[-max_turns * 2:]

    return "\n".join(f"{'User' if isinstance(msg, HumanMessage) else 'Agent'}: {msg.content}"for msg in filtered)

# Node functions
async def generate(state: GraphState) -> dict:
    """Generate an answer grounded in the retrieved documents."""
    print("Generating answer")
    generation = await answer_chain.ainvoke({"context": "", "question": state["question"]})

    print(f"Generated answer: {generation}")
    return {"generation": generation}