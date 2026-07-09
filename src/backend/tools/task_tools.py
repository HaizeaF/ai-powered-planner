"""LangChain tools that let the chatbot agent manage tasks."""
from datetime import date, datetime
from typing import Optional
from langchain.tools import tool, ToolRuntime
from src.backend.schemas.context import Context
from src.backend.models.task import TaskCreate, TaskUpdate
from src.backend.schemas.enums import RecurrenceType, TaskType
from src.backend.services.task_service import TaskService

@tool
async def create_task(title: str, start_datetime: str, runtime: ToolRuntime[Context], description: Optional[str] = None, end_datetime: Optional[str] = None, task_type: str = "task", recurrence: str = "none", project_id: Optional[int] = None) -> str:
    """Create a new task or event."""
    service = TaskService(runtime.context.session)
    data = TaskCreate(
        title=title,
        description=description,
        start_datetime=datetime.fromisoformat(start_datetime),
        end_datetime=datetime.fromisoformat(end_datetime) if end_datetime else None,
        type=TaskType(task_type),
        recurrence=RecurrenceType(recurrence),
        project_id=project_id,
    )
    created = await service.create(data)

    return f"Task '{created.title}' created with id {created.id}."

@tool
async def complete_task(task_id: int, runtime: ToolRuntime[Context]) -> str:
    """Mark a task as completed."""
    service = TaskService(runtime.context.session)
    task = await service.get(task_id)
    if task is None:
        return f"Task {task_id} not found."
    await service.update(task, TaskUpdate(completed=True))

    return f"Task {task_id} marked as completed."

@tool
async def update_task(task_id: int, runtime: ToolRuntime[Context], title: Optional[str] = None, description: Optional[str] = None, start_datetime: Optional[str] = None, end_datetime: Optional[str] = None, recurrence: Optional[str] = None, project_id: Optional[int] = None) -> str:
    """Update fields of an existing task. Only provided fields are changed."""
    service = TaskService(runtime.context.session)
    task = await service.get(task_id)
    if task is None:
        return f"Task {task_id} not found."

    fields = {
        "title": title,
        "description": description,
        "start_datetime": datetime.fromisoformat(start_datetime) if start_datetime else None,
        "end_datetime": datetime.fromisoformat(end_datetime) if end_datetime else None,
        "recurrence": RecurrenceType(recurrence) if recurrence else None,
        "project_id": project_id,
    }
    data = TaskUpdate(**{key: value for key, value in fields.items() if value is not None})
    await service.update(task, data)

    return f"Task {task_id} updated."

@tool
async def assign_task_to_project(task_id: int, project_id: int, runtime: ToolRuntime[Context]) -> str:
    """Assign an existing task to a project."""
    service = TaskService(runtime.context.session)
    task = await service.get(task_id)
    if task is None:
        return f"Task {task_id} not found."
    await service.update(task, TaskUpdate(project_id=project_id))

    return f"Task {task_id} assigned to project {project_id}."

@tool
async def list_tasks(runtime: ToolRuntime[Context], task_date: Optional[str] = None, project_id: Optional[int] = None) -> str:
    """List tasks, optionally filtered by day and/or project."""
    service = TaskService(runtime.context.session)
    if task_date is not None:
        tasks = await service.get_by_day(date.fromisoformat(task_date))
    else:
        tasks = await service.get_all()

    if project_id is not None:
        tasks = [task for task in tasks if task.project_id == project_id]

    if not tasks:
        return "No tasks found."

    return "\n".join(f"[{task.id}] {task.title} ({task.start_datetime.isoformat()}) " f"{'✓' if task.completed else ''}" for task in tasks)

@tool
async def delete_task(task_id: int, runtime: ToolRuntime[Context]) -> str:
    """Delete a task."""
    service = TaskService(runtime.context.session)
    task = await service.get(task_id)
    if task is None:
        return f"Task {task_id} not found."
    await service.delete(task)

    return f"Task {task_id} deleted."

TASK_TOOLS = [create_task, complete_task, update_task, assign_task_to_project, list_tasks, delete_task]