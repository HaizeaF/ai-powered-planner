"""Service responsible for task-related business logic."""

from datetime import date, datetime, time, timedelta
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from src.backend.models.task import Task, TaskCreate, TaskUpdate

class TaskService:
    def __init__(self, session: AsyncSession) -> None:
        """Initialize the service with a database session."""
        self.session = session

    async def create(self, task_create: TaskCreate) -> Task:
        """Create a new task."""
        task = Task.model_validate(task_create)

        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task, attribute_names=["project"])

        return task

    async def get(self, task_id: int) -> Task | None:
        """Retrieve a task by its identifier."""
        statement = (
            select(Task)
            .options(selectinload(Task.project)) # type: ignore[arg-type]
            .execution_options(populate_existing=True)
        )

        result = await self.session.scalars(statement)
        return result.first()

    async def get_all(self) -> list[Task]:
        """Retrieve all tasks."""
        statement = (
            select(Task)
            .options(selectinload(Task.project)) # type: ignore[arg-type]
            .execution_options(populate_existing=True)
        )
        result = await self.session.scalars(statement)

        return list(result)

    async def get_by_day(self, task_date: date) -> list[Task]:
        """Retrieve all tasks scheduled for a specific day."""
        start = datetime.combine(task_date, time.min)
        end = start + timedelta(days=1)

        statement = (
            select(Task)
            .where(Task.start_datetime >= start)
            .where(Task.start_datetime < end)
            .options(selectinload(Task.project))  # type: ignore[arg-type]
            .execution_options(populate_existing=True)
        )
        result = await self.session.scalars(statement)

        return list(result)

    async def update(self, task: Task, task_update: TaskUpdate) -> Task:
        """Update an existing task."""
        values = task_update.model_dump(exclude_unset=True)

        for key, value in values.items():
            setattr(task, key, value)

        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task, attribute_names=["project"])

        return task

    async def delete(self, task: Task) -> None:
        """Delete a task."""
        await self.session.delete(task)
        await self.session.commit()