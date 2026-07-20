"""Service responsible for project-related business logic."""
import logging
from sqlmodel import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from src.backend.models.project import Project, ProjectCreate, ProjectUpdate

logger = logging.getLogger(__name__)

class ProjectService:
    """Service responsible for project-related business logic."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the service with a database session."""
        self.session = session

    async def create(self, project_create: ProjectCreate) -> Project:
        """Create a new project."""
        project = Project.model_validate(project_create)

        self.session.add(project)
        await self._persist(project)

        logger.info("Created project %r (id=%s)", project.name, project.id)

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
        project = result.first()

        logger.debug("Fetched project id=%s -> %s", project_id, "found" if project else "not found")

        return project

    async def get_all(self) -> list[Project]:
        """Retrieve all projects."""
        statement = (
            select(Project)
            .options(selectinload(Project.tasks)) # type: ignore[arg-type]
            .execution_options(populate_existing=True)
        )
        result = await self.session.scalars(statement)
        projects = list(result)

        logger.debug("Fetched %d projects", len(projects))

        return projects

    async def update(self, project: Project, project_update: ProjectUpdate) -> Project:
        """Update an existing project."""
        values = project_update.model_dump(exclude_unset=True)

        for key, value in values.items():
            setattr(project, key, value)

        self.session.add(project)
        await self._persist(project)

        logger.info("Updated project %r (id=%s), fields=%s", project.name, project.id, list(values))

        return project

    async def delete(self, project: Project) -> None:
        """Delete a project and all its associated tasks."""
        await self.session.refresh(project, attribute_names=["tasks"])
        task_count = len(project.tasks)

        for task in project.tasks:
            await self.session.delete(task)

        await self.session.delete(project)

        logger.info("Deleted project %r (id=%s) and its %d tasks", project.name, project.id, task_count)

    async def _persist(self, project: Project) -> None:
        """Flush the pending write and reload the tasks relationship."""
        await self.session.flush()
        await self.session.refresh(project, attribute_names=["tasks"])