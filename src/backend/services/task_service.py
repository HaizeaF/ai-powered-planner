"""Service responsible for task-related business logic."""
import logging
from datetime import date, datetime, time, timedelta
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from src.backend.models.task import Task, TaskCreate, TaskUpdate

logger = logging.getLogger(__name__)

class TaskService:
    """Service responsible for task-related business logic."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the service with a database session."""
        self.session = session

    async def create(self, task_create: TaskCreate) -> Task:
        """Create a new task."""
        task = Task.model_validate(task_create)

        self.session.add(task)

        await self._persist(task)

        logger.info("Created task %r (id=%s)", task.title, task.id)

        return task

    async def get(self, task_id: int) -> Task | None:
        """Retrieve a task by its identifier."""
        statement = (
            select(Task)
            .where(Task.id == task_id)
            .options(selectinload(Task.project)) # type: ignore[arg-type]
            .execution_options(populate_existing=True)
        )
        result = await self.session.scalars(statement)
        task = result.first()

        logger.debug("Fetched task id=%s -> %s", task_id, "found" if task else "not found")

        return task

    async def get_all(self) -> list[Task]:
        """Retrieve all tasks."""
        statement = (
            select(Task)
            .options(selectinload(Task.project)) # type: ignore[arg-type]
            .execution_options(populate_existing=True)
        )
        result = await self.session.scalars(statement)
        tasks = list(result)

        logger.debug("Fetched %d tasks", len(tasks))

        return tasks

    async def get_by_day(self, task_date: date) -> list[Task]:
        """Retrieve all tasks scheduled for a specific day."""
        start = datetime.combine(task_date, time.min)
        end = start + timedelta(days=1)

        statement = (
            select(Task)
            .where(Task.start_datetime >= start)
            .where(Task.start_datetime < end)
            .options(selectinload(Task.project)) # type: ignore[arg-type]
            .execution_options(populate_existing=True)
        )
        result = await self.session.scalars(statement)
        tasks = list(result)

        logger.debug("Fetched %d tasks for %s", len(tasks), task_date.isoformat())

        return tasks

    async def update(self, task: Task, task_update: TaskUpdate) -> Task:
        """Update an existing task."""
        values = task_update.model_dump(exclude_unset=True)

        for key, value in values.items():
            setattr(task, key, value)

        self.session.add(task)
        await self._persist(task)

        logger.info("Updated task %r (id=%s), fields=%s", task.title, task.id, list(values))

        return task

    async def delete(self, task: Task) -> None:
        """Delete a task."""
        await self.session.delete(task)

        logger.info("Deleted task %r (id=%s)", task.title, task.id)

    async def _persist(self, task: Task) -> None:
        """Flush the pending write and reload the project relationship."""
        await self.session.flush()
        await self.session.refresh(task, attribute_names=["project"])
        if task.project is not None:
            await self.session.refresh(task.project, attribute_names=["tasks"])