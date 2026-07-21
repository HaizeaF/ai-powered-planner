"""Node functions for the assistant's conversational graph."""
import re
import logging
from langchain_core.messages import AIMessage
from langgraph.runtime import Runtime
from src.backend.chatbot.chains import tool_agent, answer_chain
from src.backend.schemas.context import Context
from src.backend.schemas.state import GraphState

logger = logging.getLogger(__name__)
_REPORT_RE = re.compile(r"STATUS:\s*(DONE|NEEDS_INFO|NEEDS_CONFIRMATION|AMBIGUOUS_MATCH|OUT_OF_SCOPE)", re.IGNORECASE)


async def run_tool_agent(state: GraphState, runtime: Runtime[Context]) -> dict:
    """Decide whether tools are needed, execute them, and produce an internal report."""
    logger.info("Running tool agent.")
    
    for msg in state["messages"]:
        print(msg.content)
        
    result = await tool_agent.ainvoke({"messages": state["messages"]}, context=runtime.context) # type: ignore[arg-type]
    report = result["messages"][-1].content

    if not _REPORT_RE.search(report or ""):
        logger.warning("Tool agent produced an invalid report: %r", report)
        report = "STATUS: NEEDS_INFO\nDETAILS: The request could not be processed, ask the user to rephrase it."

    logger.info("Tool agent report: %r", report)

    return {"tool_report": report}

async def run_answer_agent(state: GraphState) -> dict:
    """Turn the tool agent's internal report into the final reply to the user."""
    logger.info("Running answer agent.")

    answer = await answer_chain.ainvoke({"messages": state["messages"], "tool_report": state["tool_report"]})

    logger.info("Agent answer: %r", answer)

    return {"messages": [AIMessage(content=answer)]}