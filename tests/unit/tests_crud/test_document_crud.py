import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from crud import document_crud as document_crud_module
from crud.document_crud import DocumentCRUD
from schemas.document_schema import DocumentUpdate


def test_get_documents_by_project_returns_documents_list():
    db = MagicMock()
    scalars_mock = MagicMock()
    expected_documents = [MagicMock(), MagicMock()]
    scalars_mock.all.return_value = expected_documents
    result_mock = MagicMock()
    result_mock.scalars.return_value = scalars_mock
    db.execute = AsyncMock(return_value=result_mock)

    result = asyncio.run(DocumentCRUD.get_documents_by_project(db, project_id=7))

    assert result == expected_documents
    db.execute.assert_awaited_once()
    result_mock.scalars.assert_called_once()
    scalars_mock.all.assert_called_once()


def test_get_document_by_id_returns_first_document():
    db = MagicMock()
    scalars_mock = MagicMock()
    expected_document = MagicMock()
    scalars_mock.first.return_value = expected_document
    result_mock = MagicMock()
    result_mock.scalars.return_value = scalars_mock
    db.execute = AsyncMock(return_value=result_mock)

    result = asyncio.run(DocumentCRUD.get_document_by_id(db, document_id=15))

    assert result == expected_document
    db.execute.assert_awaited_once()
    result_mock.scalars.assert_called_once()
    scalars_mock.first.assert_called_once()


def test_create_document_adds_commits_and_refreshes(monkeypatch):
    db = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    class FakeDocument:
        def __init__(self, project_id: int, name: str, content: str):
            self.project_id = project_id
            self.name = name
            self.content = content

    monkeypatch.setattr(document_crud_module, "Document", FakeDocument)

    result = asyncio.run(
        DocumentCRUD.create_document(
            db,
            project_id=4,
            name="requirements.pdf",
            content="file content",
        )
    )

    assert isinstance(result, FakeDocument)
    assert result.project_id == 4
    assert result.name == "requirements.pdf"
    assert result.content == "file content"
    db.add.assert_called_once_with(result)
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(result)


def test_update_document_returns_none_when_not_found(monkeypatch):
    db = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    monkeypatch.setattr(
        DocumentCRUD,
        "get_document_by_id",
        AsyncMock(return_value=None),
    )

    result = asyncio.run(
        DocumentCRUD.update_document(
            db,
            document_id=99,
            document=DocumentUpdate(name="new", content="new content"),
        )
    )

    assert result is None
    db.commit.assert_not_awaited()
    db.refresh.assert_not_awaited()


def test_update_document_updates_all_fields(monkeypatch):
    db = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    existing = SimpleNamespace(name="old name", content="old content")
    monkeypatch.setattr(
        DocumentCRUD,
        "get_document_by_id",
        AsyncMock(return_value=existing),
    )

    result = asyncio.run(
        DocumentCRUD.update_document(
            db,
            document_id=12,
            document=DocumentUpdate(name="new name", content="new content"),
        )
    )

    assert result is existing
    assert existing.name == "new name"
    assert existing.content == "new content"
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(existing)


def test_update_document_updates_only_provided_fields(monkeypatch):
    db = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    existing = SimpleNamespace(name="kept name", content="old content")
    monkeypatch.setattr(
        DocumentCRUD,
        "get_document_by_id",
        AsyncMock(return_value=existing),
    )

    result = asyncio.run(
        DocumentCRUD.update_document(
            db,
            document_id=13,
            document=DocumentUpdate(content="updated only content"),
        )
    )

    assert result is existing
    assert existing.name == "kept name"
    assert existing.content == "updated only content"
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(existing)


def test_delete_document_returns_none_when_not_found(monkeypatch):
    db = MagicMock()
    db.delete = AsyncMock()
    db.commit = AsyncMock()
    monkeypatch.setattr(
        DocumentCRUD,
        "get_document_by_id",
        AsyncMock(return_value=None),
    )

    result = asyncio.run(DocumentCRUD.delete_document(db, document_id=404))

    assert result is None
    db.delete.assert_not_awaited()
    db.commit.assert_not_awaited()


def test_delete_document_deletes_and_commits(monkeypatch):
    db = MagicMock()
    db.delete = AsyncMock()
    db.commit = AsyncMock()
    existing = SimpleNamespace(name="doc", content="content")
    monkeypatch.setattr(
        DocumentCRUD,
        "get_document_by_id",
        AsyncMock(return_value=existing),
    )

    result = asyncio.run(DocumentCRUD.delete_document(db, document_id=1))

    assert result is True
    db.delete.assert_awaited_once_with(existing)
    db.commit.assert_awaited_once()
