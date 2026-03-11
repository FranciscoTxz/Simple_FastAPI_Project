from schemas.document_schema import FileSerializer
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models.user_model import User
from schemas.project_schema import (
    ProjectCreate,
    ProjectUpdate,
)
from schemas.user_project_schema import UserProjectCreate
from crud.project_crud import ProjectCRUD
from crud.user_project_crud import UserProjectCRUD
from crud.document_crud import DocumentCRUD
from crud.user_crud import UserCRUD


class ProjectService:
    @staticmethod
    async def get_projects(user: User, db: AsyncSession):
        db_projects = await UserProjectCRUD.get_user_projects(db, user.email)
        if not db_projects:
            raise HTTPException(
                status_code=404, detail="No projects found for the user"
            )
        return db_projects

    @staticmethod
    async def create_project(
        project: ProjectCreate,
        user: User,
        db: AsyncSession,
    ):
        db_project = await ProjectCRUD.get_project_by_name(db, name=project.name)
        if db_project:
            raise HTTPException(status_code=400, detail="Project already exists")

        project_resp = await ProjectCRUD.create_project(db, project)
        await UserProjectCRUD.create_user_project(
            db,
            UserProjectCreate(
                user_email=user.email, project_id=project_resp.id, is_owner=True
            ),
        )
        return {
            "message": f"Project created by {user.email}, Project Name: {project_resp.name}, ID: {project_resp.id}"
        }

    @staticmethod
    async def get_project_info(project_id: int, user: User, db: AsyncSession):
        db_project = await UserProjectCRUD.is_project_from_user(
            db, user.email, project_id
        )
        return db_project.project

    @staticmethod
    async def update_project(
        project_id: int, project: ProjectUpdate, user: User, db: AsyncSession
    ):
        db_user_project = await UserProjectCRUD.is_project_from_user(
            db, user.email, project_id
        )
        if not db_user_project.is_owner:
            raise HTTPException(status_code=404, detail="Project not found")
        updated_project = await ProjectCRUD.update_project(
            db, project_id, name=project.name, description=project.description
        )
        return updated_project

    @staticmethod
    async def delete_project(project_id: int, user: User, db: AsyncSession):
        db_user_project = await UserProjectCRUD.is_project_from_user(
            db, user.email, project_id
        )
        if not db_user_project.is_owner:
            raise HTTPException(status_code=404, detail="Project not found")
        await ProjectCRUD.delete_project(db, project_id)
        return

    @staticmethod
    async def get_project_documents(project_id: int, user: User, db: AsyncSession):
        await UserProjectCRUD.is_project_from_user(db, user.email, project_id)
        documents = await DocumentCRUD.get_documents_by_project(db, project_id)
        if not documents:
            raise HTTPException(
                status_code=404, detail="No documents found for project"
            )
        return documents

    @staticmethod
    async def create_project_document(
        project_id: int, file: FileSerializer, user: User, db: AsyncSession
    ):
        await UserProjectCRUD.is_project_from_user(db, user.email, project_id)

        new_document = await DocumentCRUD.create_document(
            db, project_id, file.file_name, file.file_content_base64
        )
        return new_document

    @staticmethod
    async def invite_user_to_project(
        project_id: int, user_email: str, user: User, db: AsyncSession
    ):
        db_user_project = await UserProjectCRUD.is_project_from_user(
            db, user.email, project_id
        )
        if not db_user_project.is_owner:
            raise HTTPException(status_code=404, detail="Project not found")
        db_user = await UserCRUD.get_user_by_email(db, user_email)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User to invite not found")
        db_user_invited_project = await UserProjectCRUD.is_project_from_user(
            db, user_email, project_id, check=False
        )
        if db_user_invited_project:
            raise HTTPException(
                status_code=400, detail="User is already a member of the project"
            )
        await UserProjectCRUD.create_user_project(
            db,
            user_project=UserProjectCreate(
                user_email=user_email, project_id=project_id, is_owner=False
            ),
        )
        return {
            "message": f"User with ID {user_email} invited to project {project_id} successfully"
        }
