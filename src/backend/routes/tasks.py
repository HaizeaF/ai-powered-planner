"""Task endpoints."""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from src.backend.db.database import get_session
from src.backend.models.task import Task, TaskCreate, TaskRead, TaskUpdate
from src.backend.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("", response_model=TaskRead)
async def create_task(task_create: TaskCreate, session: AsyncSession = Depends(get_session)) -> Task:
    """Create a new task."""
    service = TaskService(session)

    return await service.create(task_create)

@router.get("", response_model=list[TaskRead])
async def list_tasks(task_date: date | None = Query(default=None), session: AsyncSession = Depends(get_session)) -> list[Task]:
    """List tasks, optionally filtered by day."""
    service = TaskService(session)
    if task_date is not None:
        return await service.get_by_day(task_date)

    return await service.get_all()

@router.get("/{task_id}", response_model=TaskRead)
async def get_task(task_id: int, session: AsyncSession = Depends(get_session)) -> Task:
    """Retrieve a single task by id."""
    service = TaskService(session)
    task = await service.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task

@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(task_id: int, task_update: TaskUpdate, session: AsyncSession = Depends(get_session)) -> Task:
    """Update an existing task."""
    service = TaskService(session)
    task = await service.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return await service.update(task, task_update)

@router.post("/{task_id}/complete", response_model=TaskRead)
async def complete_task(task_id: int, session: AsyncSession = Depends(get_session)) -> Task:
    """Mark a task as completed."""
    service = TaskService(session)
    task = await service.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return await service.update(task, TaskUpdate(completed=True))

@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: int, session: AsyncSession = Depends(get_session)) -> None:
    """Delete a task."""
    service = TaskService(session)
    task = await service.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    await service.delete(task)