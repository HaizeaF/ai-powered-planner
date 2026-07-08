"""FastAPI application entry point for the chatbot."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from src.backend.chatbot.agent import create_answer_agent
from src.backend.routes import chat as chat_router
from src.backend.routes import health as health_router
from src.backend.routes import projects as projects_router
from src.backend.routes import tasks as tasks_router
from src.backend.db.database import init_db
from src.backend.config.config import Config
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    async with AsyncSqliteSaver.from_conn_string(Config.CHECKPOINT_DB_PATH) as checkpointer:
        app.state.agent = create_answer_agent(checkpointer)
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[""],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(chat_router.router)
app.include_router(health_router.router)
app.include_router(projects_router.router)
app.include_router(tasks_router.router)