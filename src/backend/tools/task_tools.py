"""LangChain tools that let the chatbot agent manage tasks."""
import logging
from datetime import date, datetime
from typing import Optional
from langchain.tools import tool, ToolRuntime
from src.backend.schemas.context import Context
from src.backend.models.task import TaskCreate, TaskUpdate
from src.backend.schemas.enums import TaskType
from src.backend.services.task_service import TaskService

logger = logging.getLogger(__name__)

@tool
async def create_task(title: str, start_datetime: str, runtime: ToolRuntime[Context], description: Optional[str] = None, type: str = "task", project_id: Optional[int] = None, is_featured: bool = False, color: str = "#7c3aed") -> str:
    """Create a standalone task or event.

    Use this tool only when the task does not belong to a project being created in the same request. If the user is creating a new project together with tasks, use create_project_with_tasks instead.
    """
    logger.info("create_task(title=%r, start_datetime=%s, project_id=%s, is_featured=%s, color=%s)", title, start_datetime, project_id, is_featured, color)

    async with runtime.context.session_lock:
        service = TaskService(runtime.context.session)
        data = TaskCreate(
                title=title,
                description=description,
                start_datetime=datetime.fromisoformat(start_datetime),
                project_id=project_id,
                type=type,
                is_featured=is_featured,
                color=color
            )
        created = await service.create(data)

        return f"Task '{created.title}' created with id {created.id}."

@tool
async def update_task(task_id: int, runtime: ToolRuntime[Context], title: Optional[str] = None, description: Optional[str] = None, start_datetime: Optional[str] = None, project_id: Optional[int] = None, type: Optional[TaskType] = None, is_featured: Optional[bool] = None, color: Optional[str] = None, completed: Optional[bool] = None) -> str:
    """Update one or more fields of an existing task.

    Use this tool to rename, reschedule, complete, reopen, feature, unfeature, change color or move an existing task.
    """
    logger.info("update_task(task_id=%s, title=%s, project_id=%s, type=%s, is_featured=%s, color=%s, completed=%s)", task_id, title, project_id, type, is_featured, color, completed)

    async with runtime.context.session_lock:
        service = TaskService(runtime.context.session)
        task = await service.get(task_id)

        if task is None:
            return f"Task {task_id} not found."

        fields = {
            "title": title,
            "description": description,
            "start_datetime": datetime.fromisoformat(start_datetime) if start_datetime else None,
            "project_id": project_id,
            "type": type,
            "is_featured": is_featured,
            "color": color
        }
        data = TaskUpdate(**{key: value for key, value in fields.items() if value is not None})
        await service.update(task, data)

        return f"Task {task_id} updated."

@tool
async def get_task(task_id: int, runtime: ToolRuntime[Context]) -> str:
    """Retrieve every detail of a single task.

    Use this tool when the user asks about one specific task.
    """
    logger.info("get_task(task_id=%s)", task_id)

    async with runtime.context.session_lock:
        service = TaskService(runtime.context.session)
        task = await service.get(task_id)

        if task is None:
            return f"Task {task_id} not found."

        return (
            f"Title: {task.title}\n"
            f"Description: {task.description or '-'}\n"
            f"Start: {task.start_datetime.isoformat()}\n"
            f"Type: {task.type}\n"
            f"Completed: {task.completed}\n"
            f"Featured: {task.is_featured}\n"
            f"Project id: {task.project_id}"
        )

@tool
async def list_tasks(runtime: ToolRuntime[Context], task_date: Optional[str] = None, project_id: Optional[int] = None) -> str:
    """List existing tasks.

    Use this tool to discover task IDs or to list standalone tasks. Do not use it
    to list the tasks of a project, use get_project instead.
    """
    logger.info("list_tasks(task_date=%s, project_id=%s)", task_date, project_id)

    async with runtime.context.session_lock:
        service = TaskService(runtime.context.session)

        if task_date is not None:
            tasks = await service.get_by_day(date.fromisoformat(task_date))
        else:
            tasks = await service.get_all()

        if project_id is not None:
            tasks = [task for task in tasks if task.project_id == project_id]

        if not tasks:
            return "No tasks found."

        return "\n".join(f"[{task.id}] {task.title} ({task.start_datetime.isoformat()}) [{'x' if task.completed else ' '}]" for task in tasks)

@tool
async def list_tasks_by_day(task_date: str, runtime: ToolRuntime[Context]) -> str:
    """List every task scheduled for a specific calendar day.

    This tool returns all tasks whose start date falls on the given date. The date must be provided in ISO format (YYYY-MM-DD). Use this tool when the user asks for tasks on a particular day, such as "today", "tomorrow", "next Monday" or a specific date.
    """
    logger.info("list_tasks_by_day(task_date=%s)", task_date)

    async with runtime.context.session_lock:
        service = TaskService(runtime.context.session)
        tasks = await service.get_by_day(date.fromisoformat(task_date))

        if not tasks:
            return "No tasks found."

        return "\n".join(
            f"[{task.id}] {task.title} ({task.start_datetime.isoformat()}) {'[x]' if task.completed else '[]'}"
            for task in tasks
        )
    
@tool
async def delete_task(task_id: int, runtime: ToolRuntime[Context]) -> str:
    """Delete an existing task.

    Use only when the user explicitly requests to remove a task.
    """
    logger.info("delete_task(task_id=%s)", task_id)

    async with runtime.context.session_lock:
        service = TaskService(runtime.context.session)
        task = await service.get(task_id)

        if task is None:
            return f"Task {task_id} not found."
        
        await service.delete(task)

        return f"Task {task_id} deleted."

TASK_TOOLS = [create_task, update_task, get_task, list_tasks, delete_task]