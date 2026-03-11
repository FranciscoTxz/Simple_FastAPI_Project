import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from crud import user_project_crud as user_project_crud_module
from crud.user_project_crud import UserProjectCRUD
from schemas.user_project_schema import UserProjectCreate


class FakeQuery:
    def options(self, *_args, **_kwargs):
        return self

    def where(self, *_args, **_kwargs):
        return self


def _patch_query_dependencies(monkeypatch):
    query = FakeQuery()

    class FakeUserProjectModel:
        project = object()
        user_email = object()
        project_id = object()

    monkeypatch.setattr(user_project_crud_module, "UserProject", FakeUserProjectModel)
    monkeypatch.setattr(
        user_project_crud_module, "select", lambda *_args, **_kwargs: query
    )
    monkeypatch.setattr(
        user_project_crud_module, "selectinload", lambda *_args, **_kwargs: object()
    )
    return query


def test_create_user_project_adds_commits_and_refreshes(monkeypatch):
    db = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    class FakeUserProject:
        def __init__(self, user_email: str, project_id: int, is_owner: bool):
            self.user_email = user_email
            self.project_id = project_id
            self.is_owner = is_owner

    monkeypatch.setattr(user_project_crud_module, "UserProject", FakeUserProject)

    payload = UserProjectCreate(
        user_email="angel@test.com",
        project_id=15,
        is_owner=True,
    )

    result = asyncio.run(UserProjectCRUD.create_user_project(db, payload))

    assert isinstance(result, FakeUserProject)
    assert result.user_email == "angel@test.com"
    assert result.project_id == 15
    assert result.is_owner is True
    db.add.assert_called_once_with(result)
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(result)


def test_get_user_projects_returns_all_user_projects(monkeypatch):
    db = MagicMock()
    scalars_mock = MagicMock()
    expected = [MagicMock(), MagicMock()]
    scalars_mock.all.return_value = expected
    result_mock = MagicMock()
    result_mock.scalars.return_value = scalars_mock
    db.execute = AsyncMock(return_value=result_mock)
    query = _patch_query_dependencies(monkeypatch)

    result = asyncio.run(UserProjectCRUD.get_user_projects(db, "angel@test.com"))

    assert result == expected
    db.execute.assert_awaited_once_with(query)
    result_mock.scalars.assert_called_once()
    scalars_mock.all.assert_called_once()


def test_is_project_from_user_returns_user_project_when_found(monkeypatch):
    db = MagicMock()
    scalars_mock = MagicMock()
    expected = MagicMock()
    scalars_mock.first.return_value = expected
    result_mock = MagicMock()
    result_mock.scalars.return_value = scalars_mock
    db.execute = AsyncMock(return_value=result_mock)
    query = _patch_query_dependencies(monkeypatch)

    result = asyncio.run(
        UserProjectCRUD.is_project_from_user(
            db,
            user_email="angel@test.com",
            project_id=8,
        )
    )

    assert result == expected
    db.execute.assert_awaited_once_with(query)
    result_mock.scalars.assert_called_once()
    scalars_mock.first.assert_called_once()


def test_is_project_from_user_raises_404_when_not_found_and_check_true(monkeypatch):
    db = MagicMock()
    scalars_mock = MagicMock()
    scalars_mock.first.return_value = None
    result_mock = MagicMock()
    result_mock.scalars.return_value = scalars_mock
    db.execute = AsyncMock(return_value=result_mock)
    _patch_query_dependencies(monkeypatch)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            UserProjectCRUD.is_project_from_user(
                db,
                user_email="angel@test.com",
                project_id=99,
                check=True,
            )
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Project not found"


def test_is_project_from_user_returns_none_when_not_found_and_check_false(monkeypatch):
    db = MagicMock()
    scalars_mock = MagicMock()
    scalars_mock.first.return_value = None
    result_mock = MagicMock()
    result_mock.scalars.return_value = scalars_mock
    db.execute = AsyncMock(return_value=result_mock)
    _patch_query_dependencies(monkeypatch)

    result = asyncio.run(
        UserProjectCRUD.is_project_from_user(
            db,
            user_email="angel@test.com",
            project_id=99,
            check=False,
        )
    )

    assert result is None
