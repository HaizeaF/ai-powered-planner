"""Project endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from src.backend.db.database import get_session
from src.backend.models.project import ProjectCreate, ProjectRead, ProjectUpdate
from src.backend.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("", response_model=ProjectRead)
async def create_project(project_create: ProjectCreate, session: AsyncSession = Depends(get_session)) -> ProjectRead:
    """Create a new project."""
    service = ProjectService(session)
    project = await service.create(project_create)

    return ProjectRead(**project.model_dump())

@router.get("", response_model=list[ProjectRead])
async def list_projects(session: AsyncSession = Depends(get_session)) -> list[ProjectRead]:
    """List all projects."""
    service = ProjectService(session)

    return [ProjectRead(**project.model_dump()) for project in await service.get_all()]

@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(project_id: int, session: AsyncSession = Depends(get_session)) -> ProjectRead:
    """Retrieve a single project by id."""
    service = ProjectService(session)
    project = await service.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return ProjectRead(**project.model_dump())

@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(project_id: int, project_update: ProjectUpdate, session: AsyncSession = Depends(get_session)) -> ProjectRead:
    """Update an existing project."""
    service = ProjectService(session)
    project = await service.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    project = await service.update(project, project_update)

    return ProjectRead(**project.model_dump())

@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: int, session: AsyncSession = Depends(get_session)) -> None:
    """Delete a project."""
    service = ProjectService(session)
    project = await service.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    await service.delete(project)