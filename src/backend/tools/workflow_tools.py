"""LangChain tools that let the chatbot agent manage multiple project/tasks operations."""
import logging
from datetime import date, datetime
from typing import Optional
from langchain.tools import tool, ToolRuntime
from src.backend.schemas.context import Context
from src.backend.models.project import ProjectCreate
from src.backend.models.task import TaskCreate
from src.backend.services.project_service import ProjectService
from src.backend.services.task_service import TaskService

logger = logging.getLogger(__name__)

@tool
async def create_project_with_tasks(name: str, tasks: list[TaskCreate], runtime: ToolRuntime[Context], color: str = "#7c3aed", description: Optional[str] = None, end_date: Optional[str] = None) -> str:
    """Create a project together with one or more tasks.
    
    Use this instead of calling create_project followed by create_task when the
    user asks to create a project together with one or more tasks. The created
    tasks are automatically linked to the newly created project.
    """
    logger.info("create_project_with_tasks(project=%r, tasks=%d)", name, len(tasks))

    async with runtime.context.session_lock:
        project_service = ProjectService(runtime.context.session)
        task_service = TaskService(runtime.context.session)

        created_project = await project_service.create(
            ProjectCreate(
                name=name,
                description=description,
                end_date=date.fromisoformat(end_date) if end_date else None,
                color=color
            )
        )

        created_tasks = []
        
        for task in tasks:
            task.project_id = created_project.id
            created_task = await task_service.create(task)

            created_tasks.append(created_task)

        task_list = ", ".join(f'"{task.title}"' for task in created_tasks)

        return (
            f'Project "{created_project.name}" created successfully. '
            f'Created {len(created_tasks)} task(s): {task_list}.'
        )

WORKFLOW_TOOLS = [create_project_with_tasks]