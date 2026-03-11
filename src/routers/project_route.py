from pydantic import EmailStr
import base64
from fastapi import Depends, APIRouter, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from models.user_model import User
from services import DatabaseConnection
from schemas.project_schema import (
    ProjectCreate,
    SuccessResponse,
    ProjectInfo,
    ProjectUpdate,
)
from schemas.user_project_schema import UserProjectWithProject
from schemas.document_schema import (
    DocumentProjectInfo,
    FileSerializer,
    DocumentProjectInfoSimple,
)
from commons.authentication import authentication_user
from services.project_service import ProjectService


router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[UserProjectWithProject])
async def get_projects(
    user: User = Depends(authentication_user),
    db: AsyncSession = Depends(DatabaseConnection().get_session),
):
    return await ProjectService.get_projects(user, db)


@router.post("", response_model=SuccessResponse, status_code=201)
async def create_project(
    project: ProjectCreate,
    user: User = Depends(authentication_user),
    db: AsyncSession = Depends(DatabaseConnection().get_session),
):
    return await ProjectService.create_project(project, user, db)


router_project = APIRouter(prefix="/project", tags=["project"])


@router_project.get("/{project_id}/info", response_model=ProjectInfo)
async def get_project_info(
    project_id: int,
    user: User = Depends(authentication_user),
    db: AsyncSession = Depends(DatabaseConnection().get_session),
):
    return await ProjectService.get_project_info(project_id, user, db)


@router_project.put("/{project_id}/info", response_model=ProjectCreate)
async def update_project(
    project_id: int,
    project: ProjectUpdate,
    user: User = Depends(authentication_user),
    db: AsyncSession = Depends(DatabaseConnection().get_session),
):
    return await ProjectService.update_project(project_id, project, user, db)


@router_project.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    user: User = Depends(authentication_user),
    db: AsyncSession = Depends(DatabaseConnection().get_session),
):
    await ProjectService.delete_project(project_id, user, db)
    return


@router_project.get(
    "/{project_id}/documents", response_model=list[DocumentProjectInfoSimple]
)
async def get_project_documents(
    project_id: int,
    user: User = Depends(authentication_user),
    db: AsyncSession = Depends(DatabaseConnection().get_session),
):
    return await ProjectService.get_project_documents(project_id, user, db)


@router_project.post(
    "/{project_id}/documents", status_code=201, response_model=DocumentProjectInfo
)
async def create_project_document(
    project_id: int,
    file: UploadFile = File(...),
    user: User = Depends(authentication_user),
    db: AsyncSession = Depends(DatabaseConnection().get_session),
):
    file_content = await file.read()
    file_content_base64 = base64.b64encode(file_content).decode("utf-8")
    file_serializer = FileSerializer(
        file_content_base64=file_content_base64,
        file_name=file.filename or "unnamed.pdf",
    )
    return await ProjectService.create_project_document(
        project_id, file_serializer, user, db
    )


@router_project.post(
    "/{project_id}/invite", status_code=200, response_model=SuccessResponse
)
async def invite_user_to_project(
    project_id: int,
    user_email: EmailStr,
    user: User = Depends(authentication_user),
    db: AsyncSession = Depends(DatabaseConnection().get_session),
):
    return await ProjectService.invite_user_to_project(project_id, user_email, user, db)
