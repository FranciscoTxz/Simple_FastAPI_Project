import asyncio
import base64
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from schemas.document_schema import FileSerializer
from services.document_service import DocumentService

if TYPE_CHECKING:
    from models.user_model import User


def _make_user(email: str = "angel@test.com") -> "User":
    return cast("User", SimpleNamespace(email=email))


def _make_pdf_b64() -> str:
    return base64.b64encode(b"%PDF" + b"a" * 10).decode()


# ---------------------------------------------------------------------------
# get_document
# ---------------------------------------------------------------------------


def test_get_document_raises_404_when_document_not_found():
    db = MagicMock()
    with patch(
        "services.document_service.DocumentCRUD.get_document_by_id",
        new=AsyncMock(return_value=None),
    ):
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(
                DocumentService.get_document(document_id=99, user=_make_user(), db=db)
            )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Document not found"


def test_get_document_returns_document_when_user_has_access():
    db = MagicMock()
    doc = SimpleNamespace(id=1, project_id=5)
    with (
        patch(
            "services.document_service.DocumentCRUD.get_document_by_id",
            new=AsyncMock(return_value=doc),
        ),
        patch(
            "services.document_service.UserProjectCRUD.is_project_from_user",
            new=AsyncMock(return_value=SimpleNamespace(is_owner=True)),
        ),
    ):
        result = asyncio.run(
            DocumentService.get_document(document_id=1, user=_make_user(), db=db)
        )

    assert result is doc


# ---------------------------------------------------------------------------
# update_document
# ---------------------------------------------------------------------------


def test_update_document_raises_404_when_document_not_found():
    db = MagicMock()
    file = FileSerializer(file_name="doc.pdf", file_content_base64=_make_pdf_b64())
    with patch(
        "services.document_service.DocumentCRUD.get_document_by_id",
        new=AsyncMock(return_value=None),
    ):
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(
                DocumentService.update_document(
                    document_id=99, file=file, user=_make_user(), db=db
                )
            )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Document not found"


def test_update_document_returns_updated_document():
    db = MagicMock()
    doc = SimpleNamespace(id=2, project_id=7)
    updated_doc = SimpleNamespace(id=2, name="doc.pdf", content=_make_pdf_b64())
    file = FileSerializer(file_name="doc.pdf", file_content_base64=_make_pdf_b64())
    with (
        patch(
            "services.document_service.DocumentCRUD.get_document_by_id",
            new=AsyncMock(return_value=doc),
        ),
        patch(
            "services.document_service.UserProjectCRUD.is_project_from_user",
            new=AsyncMock(return_value=SimpleNamespace(is_owner=True)),
        ),
        patch(
            "services.document_service.DocumentCRUD.update_document",
            new=AsyncMock(return_value=updated_doc),
        ),
    ):
        result = asyncio.run(
            DocumentService.update_document(
                document_id=2, file=file, user=_make_user(), db=db
            )
        )

    assert result is updated_doc


# ---------------------------------------------------------------------------
# delete_document
# ---------------------------------------------------------------------------


def test_delete_document_raises_404_when_document_not_found():
    db = MagicMock()
    with patch(
        "services.document_service.DocumentCRUD.get_document_by_id",
        new=AsyncMock(return_value=None),
    ):
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(
                DocumentService.delete_document(
                    document_id=99, user=_make_user(), db=db
                )
            )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Document not found"


def test_delete_document_raises_404_when_user_is_not_owner():
    db = MagicMock()
    doc = SimpleNamespace(id=3, project_id=10)
    with (
        patch(
            "services.document_service.DocumentCRUD.get_document_by_id",
            new=AsyncMock(return_value=doc),
        ),
        patch(
            "services.document_service.UserProjectCRUD.is_project_from_user",
            new=AsyncMock(return_value=SimpleNamespace(is_owner=False)),
        ),
    ):
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(
                DocumentService.delete_document(document_id=3, user=_make_user(), db=db)
            )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Document not found"


def test_delete_document_succeeds_when_owner():
    db = MagicMock()
    doc = SimpleNamespace(id=4, project_id=12)
    delete_mock = AsyncMock(return_value=True)
    with (
        patch(
            "services.document_service.DocumentCRUD.get_document_by_id",
            new=AsyncMock(return_value=doc),
        ),
        patch(
            "services.document_service.UserProjectCRUD.is_project_from_user",
            new=AsyncMock(return_value=SimpleNamespace(is_owner=True)),
        ),
        patch(
            "services.document_service.DocumentCRUD.delete_document",
            new=delete_mock,
        ),
    ):
        result = asyncio.run(
            DocumentService.delete_document(document_id=4, user=_make_user(), db=db)
        )

    assert result is None
    delete_mock.assert_awaited_once_with(db, 4)
