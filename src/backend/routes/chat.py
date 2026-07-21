"""Chat endpoint that runs a conversational turn through the agent."""
import logging
import asyncio
from langchain_core.messages import HumanMessage
from fastapi import APIRouter, Request, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from src.backend.schemas.message import MessageRequest, MessageResponse
from src.backend.schemas.context import Context
from src.backend.db.database import get_session
from src.backend.config.config import Config

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/chat", response_model=MessageResponse)
async def chat(request: Request, body: MessageRequest, session: AsyncSession = Depends(get_session)) -> MessageResponse:
    """Run a single conversational turn through the chatbot graph."""
    logger.info("Chat turn started (thread_id=%s): %r", body.thread_id, body.question)

    graph = request.app.state.graph
    try:
        result = await asyncio.wait_for(
            graph.ainvoke(
                {"messages": [HumanMessage(content=body.question)], "tool_report": ""},
                context=Context(session=session),
                config={"configurable": {"thread_id": body.thread_id}}
            ),
            timeout=Config.CHAT_TIMEOUT_SECONDS
        )
    except:
        logger.warning("Chat turn timed out after %ss (thread_id=%s)", Config.CHAT_TIMEOUT_SECONDS, body.thread_id)

        return MessageResponse(agent_response="Sorry, an unexpected error has ocurred. Please try again.")

    answer = result["messages"][-1].content

    logger.info("Chat turn finished (thread_id=%s): %r", body.thread_id, answer)

    return MessageResponse(agent_response=answer)
