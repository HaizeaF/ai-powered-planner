"""LangChain tools that let the chatbot agent manage projects."""
from datetime import date
from typing import Optional
from langchain.tools import tool, ToolRuntime
from src.backend.schemas.context import Context
from src.backend.models.project import ProjectCreate, ProjectUpdate
from src.backend.services.project_service import ProjectService

@tool
async def create_project(name: str, runtime: ToolRuntime[Context], description: Optional[str] = None, end_date: Optional[str] = None) -> str:
    """Create a new project."""
    service = ProjectService(runtime.context.session)
    data = ProjectCreate(
        name=name,
        description=description,
        end_date=date.fromisoformat(end_date) if end_date else None,
    )
    created = await service.create(data)

    return f"Project '{created.name}' created with id {created.id}."

@tool
async def update_project(project_id: int, runtime: ToolRuntime[Context], name: Optional[str] = None, description: Optional[str] = None, end_date: Optional[str] = None) -> str:
    """Update fields of an existing project. Only provided fields are changed."""
    service = ProjectService(runtime.context.session)
    project = await service.get(project_id)
    if project is None:
        return f"Project {project_id} not found."

    fields = {
        "name": name,
        "description": description,
        "end_date": date.fromisoformat(end_date) if end_date else None,
    }
    data = ProjectUpdate(**{key: value for key, value in fields.items() if value is not None})
    await service.update(project, data)

    return f"Project {project_id} updated."

@tool
async def list_projects(runtime: ToolRuntime[Context]) -> str:
    """List all projects with their completion progress."""
    service = ProjectService(runtime.context.session)
    projects = await service.get_all()
    if not projects:
        return "No projects found."

    return "\n".join(f"[{project.id}] {project.name} - {service.calculate_progress(project):.0%} completed" for project in projects)


@tool
async def delete_project(project_id: int, runtime: ToolRuntime[Context]) -> str:
    """Delete a project and all its associated tasks."""
    service = ProjectService(runtime.context.session)
    project = await service.get(project_id)
    if project is None:
        return f"Project {project_id} not found."
    await service.delete(project)

    return f"Project {project_id} and its tasks were deleted."

PROJECT_TOOLS = [create_project, update_project, list_projects, delete_project]