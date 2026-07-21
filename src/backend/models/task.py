"""Task model."""
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from src.backend.schemas.enums import TaskType, ColorType
if TYPE_CHECKING:
    from src.backend.models.project import Project, ProjectRead

class TaskBase(SQLModel):
    """Common fields for a task, shared between creation and reading."""
    title: str
    description: Optional[str] = None
    start_datetime: datetime
    type: str = TaskType.TASK
    is_featured: bool = False
    color: str = ColorType.PURPLE
    project_id: Optional[int] = Field(default=None, foreign_key="project.id")

class Task(TaskBase, table=True):
    """Task persisted in the database."""
    id: Optional[int] = Field(default=None, primary_key=True)
    completed: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    project: Optional["Project"] = Relationship(back_populates="tasks")

class TaskCreate(TaskBase):
    """Payload for creating a task."""
    pass

class TaskUpdate(SQLModel):
    """Payload for updating a task. All fields are optional."""
    title: Optional[str] = None
    description: Optional[str] = None
    start_datetime: Optional[datetime] = None
    type: Optional[str] = None
    is_featured: Optional[bool] = None
    color: Optional[str] = None
    project_id: Optional[int] = None
    completed: Optional[bool] = None

class TaskRead(TaskBase):
    """Payload for reading a task."""
    id: int
    completed: bool
    created_at: datetime
    project: Optional["ProjectRead"] = None