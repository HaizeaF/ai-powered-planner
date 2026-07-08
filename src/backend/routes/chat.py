"""Chat endpoint that runs a conversational turn through the graph."""
from langchain_core.messages import HumanMessage, AIMessage
from fastapi import APIRouter, Request
from sqlmodel.ext.asyncio.session import AsyncSession
from src.backend.db.database import engine
from src.backend.schemas.message import MessageRequest, MessageResponse
from src.backend.schemas.context import Context

router = APIRouter()

@router.post("/chat", response_model=MessageResponse)
async def chat(request: Request, body: MessageRequest) -> MessageResponse:
    """Run a single conversational turn through the chatbot graph."""

    agent = request.app.state.answer_agent
    async with AsyncSession(engine, expire_on_commit=False) as session:
        result = await agent.ainvoke(
            {"messages": [HumanMessage(content=body.question)]},
            context=Context(session=session),
            config={"configurable": {"thread_id": body.thread_id}}
        )

    return MessageResponse(agent_response=result["messages"][-1].content)