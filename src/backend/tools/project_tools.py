"""LangChain tools that let the chatbot agent manage projects."""
import logging
from datetime import date
from typing import Optional
from langchain.tools import tool, ToolRuntime
from src.backend.schemas.context import Context
from src.backend.models.project import ProjectCreate, ProjectUpdate
from src.backend.services.project_service import ProjectService

logger = logging.getLogger(__name__)

@tool
async def create_project(name: str, runtime: ToolRuntime[Context], description: Optional[str] = None, end_date: Optional[str] = None, color: str = "#7c3aed") -> str:
    """Create a new standalone project.

    Use this tool only when the user wants to create a project without creating tasks at the same time. If the request includes one or more tasks belonging to the new project, use create_project_with_tasks instead.
    """
    logger.info("create_project(name=%r, end_date=%s, color=%s)", name, end_date, color)

    async with runtime.context.session_lock:
        service = ProjectService(runtime.context.session)
        data = ProjectCreate(
                name=name,
                description=description,
                end_date=date.fromisoformat(end_date) if end_date else None,
                color=color
            )
        created = await service.create(data)

        return f"Project '{created.name}' created with id {created.id}."

@tool
async def update_project(project_id: int, runtime: ToolRuntime[Context], name: Optional[str] = None, description: Optional[str] = None, end_date: Optional[str] = None, color: str = "#7c3aed") -> str:
    """Update one or more fields of an existing project.

    Only the provided fields are modified. Use this tool whenever the user wants to rename a project, change its description, deadline or color.
    """
    logger.info("update_project(project_id=%s, name=%s, end_date=%s, color=%s)", project_id, name, end_date, color)

    async with runtime.context.session_lock:
        service = ProjectService(runtime.context.session)
        project = await service.get(project_id)

        if project is None:
            return f"Project {project_id} not found."

        fields = {
            "name": name,
            "description": description,
            "end_date": date.fromisoformat(end_date) if end_date else None,
            "color": color
        }
        data = ProjectUpdate(**{key: value for key, value in fields.items() if value is not None})
        await service.update(project, data)

        return f"Project {project_id} updated."

@tool
async def get_project(project_id: int, runtime: ToolRuntime[Context]) -> str:
    """Retrieve a project together with all of its tasks.

    Prefer this tool whenever the user asks about a specific project or wants to list the tasks belonging to a project.
    """
    logger.info("get_project(project_id=%s)", project_id)

    async with runtime.context.session_lock:
        service = ProjectService(runtime.context.session)
        project = await service.get(project_id)

        if project is None:
            return f"Project {project_id} not found."
        
        tasks = "\n".join(f"- [{'x' if task.completed else ' '}] {task.title} ({task.type})" for task in project.tasks)

        return (
            f"Name: {project.name}\n"
            f"Description: {project.description or '-'}\n"
            f"End date: {project.end_date.isoformat() if project.end_date else '-'}\n"
            f"Color: {project.color}\n"
            f"Tasks:\n{tasks or '-'}"
        )

@tool
async def list_projects(runtime: ToolRuntime[Context]) -> str:
    """List every existing project.

    Use this tool to discover project IDs or when the user asks for an overview of all projects.
    """
    logger.info("list_projects()")

    async with runtime.context.session_lock:
        service = ProjectService(runtime.context.session)
        projects = await service.get_all()

        if not projects:
            return "No projects found."

        lines = []
        for project in projects:
            completed = sum(1 for task in project.tasks if task.completed)
            lines.append(f"[{project.id}] {project.name} - {completed}/{len(project.tasks)} tasks completed")

        return "\n".join(lines)

@tool
async def delete_project(project_id: int, runtime: ToolRuntime[Context]) -> str:
    """Delete an existing project and every task that belongs to it.

    Use only when the user explicitly wants to remove a project.
    """
    logger.info("delete_project(project_id=%s)", project_id)

    async with runtime.context.session_lock:
        service = ProjectService(runtime.context.session)
        project = await service.get(project_id)

        if project is None:
            return f"Project {project_id} not found."
        
        await service.delete(project)

        return f"Project {project_id} and its tasks were deleted."

PROJECT_TOOLS = [create_project, update_project, get_project, list_projects, delete_project]