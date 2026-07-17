"""Service responsible for project-related business logic."""

from sqlmodel import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from src.backend.models.project import Project, ProjectCreate, ProjectUpdate
from src.backend.schemas.enums import TaskType

class ProjectService:
    """Service responsible for project-related business logic."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the service with a database session."""
        self.session = session

    async def create(self, project_create: ProjectCreate) -> Project:
        """Create a new project."""
        project = Project.model_validate(project_create)

        self.session.add(project)
        await self.session.flush() 
        await self.session.refresh(project, attribute_names=["tasks"])

        return project

    async def get(self, project_id: int) -> Project | None:
        """Retrieve a project by its identifier."""
        statement = (
            select(Project)
            .where(Project.id == project_id)
            .options(selectinload(Project.tasks)) # type: ignore[arg-type]
            .execution_options(populate_existing=True)
        )
        result = await self.session.scalars(statement)

        return result.first()

    async def get_all(self) -> list[Project]:
        """Retrieve all projects."""
        statement = (
            select(Project)
            .options(selectinload(Project.tasks)) # type: ignore[arg-type]
            .execution_options(populate_existing=True)
        )
        result = await self.session.scalars(statement)

        return list(result)

    async def update(self, project: Project, project_update: ProjectUpdate) -> Project:
        """Update an existing project."""
        values = project_update.model_dump(exclude_unset=True)

        for key, value in values.items():
            setattr(project, key, value)

        self.session.add(project)
        await self.session.flush() 
        await self.session.refresh(project, attribute_names=["tasks"])

        return project

    async def delete(self, project: Project) -> None:
        """Delete a project and all its associated tasks."""
        await self.session.refresh(project, attribute_names=["tasks"])

        for task in project.tasks:
            await self.session.delete(task) # TODO: Alembic no incluye delete en cascada? 

        await self.session.delete(project)