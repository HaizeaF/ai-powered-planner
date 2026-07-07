"""Service responsible for project-related business logic."""

from sqlmodel import Session, select
from src.backend.models.project import (Project, ProjectCreate, ProjectUpdate)
from src.backend.schemas.enums import TaskType

class ProjectService:
    """Service responsible for project-related business logic."""

    def __init__(self, session: Session) -> None:
        """Initialize the service with a database session."""
        self.session = session

    def create(self, project_create: ProjectCreate) -> Project:
        """Create a new project."""
        project = Project.model_validate(project_create)

        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)

        return project

    def get(self, project_id: int) -> Project | None:
        """Retrieve a project by its identifier."""
        return self.session.get(Project, project_id)

    def get_all(self) -> list[Project]:
        """Retrieve all projects."""
        statement = select(Project)

        return list(self.session.exec(statement).all())

    def update(self, project: Project, project_update: ProjectUpdate) -> Project:
        """Update an existing project."""
        values = project_update.model_dump(exclude_unset=True)

        for key, value in values.items():
            setattr(project, key, value)

        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)

        return project

    def delete(self, project: Project) -> None:
        """Delete a project and all its associated tasks."""
        for task in project.tasks:
            self.session.delete(task)
        self.session.delete(project)
        self.session.commit()


    @staticmethod
    def calculate_progress(project: Project) -> float:
        """Calculate the completion percentage of a project.

        Only tasks of type 'task' are considered. Events are ignored because
        they cannot be completed.
        """
        tasks = [task for task in project.tasks if task.type == TaskType.TASK]

        if not tasks:
            return 0.0

        completed = sum(task.completed for task in tasks)

        return completed / len(tasks)