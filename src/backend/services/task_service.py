"""Service responsible for task-related business logic."""

from datetime import date, datetime, time, timedelta
from sqlmodel import Session, select
from src.backend.models.task import Task, TaskCreate, TaskUpdate

class TaskService:
    def __init__(self, session: Session) -> None:
        """Initialize the service with a database session."""
        self.session = session

    def create(self, task_create: TaskCreate) -> Task:
        """Create a new task."""
        task = Task.model_validate(task_create)

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        return task

    def get(self, task_id: int) -> Task | None:
        """Retrieve a task by its identifier."""
        return self.session.get(Task, task_id)

    def get_all(self) -> list[Task]:
        """Retrieve all tasks."""
        statement = select(Task)

        return list(self.session.exec(statement).all())

    def get_by_day(self, task_date: date) -> list[Task]:
        """Retrieve all tasks scheduled for a specific day."""
        start = datetime.combine(task_date, time.min)
        end = start + timedelta(days=1)

        statement = (
            select(Task)
            .where(Task.start_datetime >= start)
            .where(Task.start_datetime < end)
        )

        return list(self.session.exec(statement).all())

    def update(self, task: Task, task_update: TaskUpdate) -> Task:
        """Update an existing task."""
        values = task_update.model_dump(exclude_unset=True)

        for key, value in values.items():
            setattr(task, key, value)

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        return task

    def delete(self, task: Task) -> None:
        """Delete a task."""
        self.session.delete(task)
        self.session.commit()