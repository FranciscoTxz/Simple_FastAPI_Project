import base64
from fastapi import Depends, APIRouter, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from models.user_model import User
from services import DatabaseConnection
from services.document_service import DocumentService
from schemas.document_schema import DocumentProjectInfo, FileSerializer
from commons.authentication import authentication_user


router = APIRouter(prefix="/document", tags=["document"])


@router.get("/{document_id}", response_model=DocumentProjectInfo)
async def get_document(
    document_id: int,
    user: User = Depends(authentication_user),
    db: AsyncSession = Depends(DatabaseConnection().get_session),
):
    return await DocumentService.get_document(document_id, user, db)


@router.put("/{document_id}", response_model=DocumentProjectInfo)
async def update_document(
    document_id: int,
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

    return await DocumentService.update_document(document_id, file_serializer, user, db)


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: int,
    user: User = Depends(authentication_user),
    db: AsyncSession = Depends(DatabaseConnection().get_session),
):
    return await DocumentService.delete_document(document_id, user, db)
