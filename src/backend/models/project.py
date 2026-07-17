"""Project model."""
from datetime import date, datetime, timezone
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel
from src.backend.schemas.enums import ColorType
from src.backend.models.task import Task
from src.backend.models.task import TaskRead

class ProjectBase(SQLModel):
    """Common fields for a project, shared between creation and reading."""
    name: str
    description: Optional[str] = None
    end_date: Optional[date] = None
    color: str = ColorType.PURPLE
    archived: bool = False

class Project(ProjectBase, table=True):
    """Project persisted in the database."""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tasks: List[Task] = Relationship(back_populates="project")

class ProjectCreate(ProjectBase):
    """Payload for creating a project."""
    pass

class ProjectUpdate(SQLModel):
    """Payload for updating a project. All fields are optional."""
    name: Optional[str] = None
    description: Optional[str] = None
    end_date: Optional[date] = None
    color: Optional[str] = None
    archived: Optional[bool] = None

class ProjectRead(ProjectBase):
    """Payload for reading a project, includes the computed progress."""
    id: int
    created_at: datetime

TaskRead.model_rebuild(_types_namespace={"ProjectRead": ProjectRead})