from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.user_project_model import UserProject
from schemas.user_project_schema import UserProjectCreate
from sqlalchemy.orm import selectinload


class UserProjectCRUD:
    @staticmethod
    async def create_user_project(db: AsyncSession, user_project: UserProjectCreate):
        db_user_project = UserProject(
            user_email=user_project.user_email,
            project_id=user_project.project_id,
            is_owner=user_project.is_owner,
        )
        db.add(db_user_project)
        await db.commit()
        await db.refresh(db_user_project)
        return db_user_project

    @staticmethod
    async def get_user_projects(db: AsyncSession, user_email: str):
        result = await db.execute(
            select(UserProject)
            .options(selectinload(UserProject.project))
            .where(UserProject.user_email == user_email)
        )
        user_projects = result.scalars().all()
        return user_projects

    @staticmethod
    async def is_project_from_user(db: AsyncSession, user_email: str, project_id: int):
        result = await db.execute(
            select(UserProject)
            .options(selectinload(UserProject.project))
            .where(
                UserProject.user_email == user_email,
                UserProject.project_id == project_id,
            )
        )
        return result.scalars().first()
