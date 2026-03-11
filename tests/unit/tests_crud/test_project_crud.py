import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from crud import project_crud as project_crud_module
from crud.project_crud import ProjectCRUD
from schemas.project_schema import ProjectCreate


def test_get_project_by_name_returns_first_project():
    db = MagicMock()
    scalars_mock = MagicMock()
    expected_project = MagicMock()
    scalars_mock.first.return_value = expected_project
    result_mock = MagicMock()
    result_mock.scalars.return_value = scalars_mock
    db.execute = AsyncMock(return_value=result_mock)

    result = asyncio.run(ProjectCRUD.get_project_by_name(db, name="AI Workspace"))

    assert result == expected_project
    db.execute.assert_awaited_once()
    result_mock.scalars.assert_called_once()
    scalars_mock.first.assert_called_once()


def test_create_project_adds_commits_and_refreshes(monkeypatch):
    db = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    class FakeProject:
        def __init__(self, name: str, description: str):
            self.name = name
            self.description = description

    monkeypatch.setattr(project_crud_module, "Project", FakeProject)

    payload = ProjectCreate(name="Planning", description="Sprint planning")
    result = asyncio.run(ProjectCRUD.create_project(db, payload))

    assert isinstance(result, FakeProject)
    assert result.name == "Planning"
    assert result.description == "Sprint planning"
    db.add.assert_called_once_with(result)
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(result)


def test_update_project_returns_none_when_not_found():
    db = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    scalars_mock = MagicMock()
    scalars_mock.first.return_value = None
    result_mock = MagicMock()
    result_mock.scalars.return_value = scalars_mock
    db.execute = AsyncMock(return_value=result_mock)

    result = asyncio.run(
        ProjectCRUD.update_project(
            db,
            project_id=999,
            name="New name",
            description="New description",
        )
    )

    assert result is None
    db.add.assert_not_called()
    db.commit.assert_not_awaited()
    db.refresh.assert_not_awaited()


def test_update_project_updates_fields_and_persists():
    db = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    existing = SimpleNamespace(name="Old", description="Old description")
    scalars_mock = MagicMock()
    scalars_mock.first.return_value = existing
    result_mock = MagicMock()
    result_mock.scalars.return_value = scalars_mock
    db.execute = AsyncMock(return_value=result_mock)

    result = asyncio.run(
        ProjectCRUD.update_project(
            db,
            project_id=10,
            name="New",
            description="New description",
        )
    )

    assert result is existing
    assert existing.name == "New"
    assert existing.description == "New description"
    db.add.assert_called_once_with(existing)
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(existing)


def test_update_project_keeps_existing_values_when_none_provided():
    db = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    existing = SimpleNamespace(name="Current", description="Current description")
    scalars_mock = MagicMock()
    scalars_mock.first.return_value = existing
    result_mock = MagicMock()
    result_mock.scalars.return_value = scalars_mock
    db.execute = AsyncMock(return_value=result_mock)

    result = asyncio.run(ProjectCRUD.update_project(db, project_id=11))

    assert result is existing
    assert existing.name == "Current"
    assert existing.description == "Current description"
    db.add.assert_called_once_with(existing)
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(existing)


def test_delete_project_returns_none_when_not_found():
    db = MagicMock()
    db.delete = AsyncMock()
    db.commit = AsyncMock()
    scalars_mock = MagicMock()
    scalars_mock.first.return_value = None
    result_mock = MagicMock()
    result_mock.scalars.return_value = scalars_mock
    db.execute = AsyncMock(return_value=result_mock)

    result = asyncio.run(ProjectCRUD.delete_project(db, project_id=404))

    assert result is None
    db.delete.assert_not_awaited()
    db.commit.assert_not_awaited()


def test_delete_project_deletes_and_commits():
    db = MagicMock()
    db.delete = AsyncMock()
    db.commit = AsyncMock()
    existing = SimpleNamespace(name="To remove", description="To remove")
    scalars_mock = MagicMock()
    scalars_mock.first.return_value = existing
    result_mock = MagicMock()
    result_mock.scalars.return_value = scalars_mock
    db.execute = AsyncMock(return_value=result_mock)

    result = asyncio.run(ProjectCRUD.delete_project(db, project_id=7))

    assert result is existing
    db.delete.assert_awaited_once_with(existing)
    db.commit.assert_awaited_once()
