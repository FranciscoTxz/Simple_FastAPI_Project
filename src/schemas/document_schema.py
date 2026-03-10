import base64
from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime


class DocumentBase(BaseModel):
    name: str
    content: str


class DocumentGet(DocumentBase):
    id: int
    project_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentProjectInfo(BaseModel):
    id: int
    name: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentProjectInfoSimple(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentUpdate(BaseModel):
    name: str | None = None
    content: str | None = None


class FileSerializer(BaseModel):
    file_content_base64: str
    file_name: str = Field(max_length=100)

    @field_validator("file_name")
    def file_must_be_pdf(cls, v: str) -> str:
        """Ensure only PDF files are allowed."""
        if not v.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        return v

    @field_validator("file_content_base64")
    def validate_file_content(cls, v: str) -> str:
        """Validate PDF content, size limits, and security."""
        try:
            file_bytes = base64.b64decode(v)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid base64 encoding")

        max_size = 2 * 1024 * 1024
        if len(file_bytes) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds 2MB limit. Current size: {len(file_bytes)} bytes, maximum: {max_size} bytes",
            )

        if not file_bytes.startswith(b"%PDF"):
            raise HTTPException(
                status_code=400, detail="File content is not a valid PDF"
            )

        dangerous_keywords = [
            b"/EmbeddedFile",
            b"/JavaScript",
            b"/JS",
            b"/Launch",
            b"/SubmitForm",
            b"/ImportData",
        ]

        for keyword in dangerous_keywords:
            if keyword in file_bytes:
                raise HTTPException(
                    status_code=400,
                    detail="PDF contains prohibited content: embedded files, JavaScript, or executable actions are not allowed",
                )

        return v
