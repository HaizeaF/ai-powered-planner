"""FastAPI application entry point for the chatbot."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from src.backend.services.graph_service import build_graph
from src.backend.routes import chat as chat_router
from src.backend.routes import health as health_router
from src.backend.routes import projects as projects_router
from src.backend.routes import tasks as tasks_router
from src.backend.config.config import Config
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSqliteSaver.from_conn_string(Config.CHECKPOINT_DB_PATH) as checkpointer:
        app.state.graph = build_graph(checkpointer)
        yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(chat_router.router)
app.include_router(health_router.router)
app.include_router(projects_router.router)
app.include_router(tasks_router.router)