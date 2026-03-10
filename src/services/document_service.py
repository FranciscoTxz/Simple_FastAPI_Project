from fastapi import HTTPException
from models.user_model import User
from crud.document_crud import DocumentCRUD
from crud.user_project_crud import UserProjectCRUD
from schemas.document_schema import DocumentUpdate, FileSerializer
from sqlalchemy.ext.asyncio import AsyncSession


class DocumentService:
    @staticmethod
    async def get_document(
        document_id: int,
        user: User,
        db: AsyncSession,
    ):
        db_document = await DocumentCRUD.get_document_by_id(db, document_id)
        if not db_document:
            raise HTTPException(status_code=404, detail="Document not found")
        db_user_project = await UserProjectCRUD.is_project_from_user(
            db, user.id, db_document.project_id
        )
        if not db_user_project:
            raise HTTPException(status_code=404, detail="Document not found")
        return db_document

    @staticmethod
    async def update_document(
        document_id: int,
        file: FileSerializer,
        user: User,
        db: AsyncSession,
    ):
        db_document = await DocumentCRUD.get_document_by_id(db, document_id)
        if not db_document:
            raise HTTPException(status_code=404, detail="Document not found")
        db_user_project = await UserProjectCRUD.is_project_from_user(
            db, user.id, db_document.project_id
        )
        if not db_user_project:
            raise HTTPException(status_code=404, detail="Document not found")
        document = DocumentUpdate(name=file.file_name, content=file.file_content_base64)
        db_document = await DocumentCRUD.update_document(db, document_id, document)
        return db_document

    @staticmethod
    async def delete_document(
        document_id: int,
        user: User,
        db: AsyncSession,
    ):
        db_document = await DocumentCRUD.get_document_by_id(db, document_id)
        if not db_document:
            raise HTTPException(status_code=404, detail="Document not found")
        db_user_project = await UserProjectCRUD.is_project_from_user(
            db, user.id, db_document.project_id
        )
        if not db_user_project:
            raise HTTPException(status_code=404, detail="Document not found")
        await DocumentCRUD.delete_document(db, document_id)
        return
