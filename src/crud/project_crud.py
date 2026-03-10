from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.project_model import Project
from schemas.project_schema import ProjectCreate


class ProjectCRUD:
    @staticmethod
    async def get_project_by_name(db: AsyncSession, name: str):
        result = await db.execute(select(Project).where(Project.name == name))
        return result.scalars().first()

    @staticmethod
    async def create_project(db: AsyncSession, project: ProjectCreate):
        db_project = Project(name=project.name, description=project.description)
        db.add(db_project)
        await db.commit()
        await db.refresh(db_project)
        return db_project

    @staticmethod
    async def update_project(
        db: AsyncSession,
        project_id: int,
        name: str | None = None,
        description: str | None = None,
    ):
        result = await db.execute(select(Project).where(Project.id == project_id))
        db_project = result.scalars().first()
        if not db_project:
            return None
        if name:
            db_project.name = name
        if description:
            db_project.description = description
        db.add(db_project)
        await db.commit()
        await db.refresh(db_project)
        return db_project

    @staticmethod
    async def delete_project(db: AsyncSession, project_id: int):
        result = await db.execute(select(Project).where(Project.id == project_id))
        db_project = result.scalars().first()
        if not db_project:
            return None
        await db.delete(db_project)
        await db.commit()
        return db_project
