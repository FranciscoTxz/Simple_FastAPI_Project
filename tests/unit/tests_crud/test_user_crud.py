import asyncio
from unittest.mock import AsyncMock, MagicMock

from crud import user_crud as user_crud_module
from crud.user_crud import UserCRUD
from schemas.user_schema import UserCreate


def test_get_user_by_email_returns_first_user():
    db = MagicMock()
    scalars_mock = MagicMock()
    expected_user = MagicMock()
    scalars_mock.first.return_value = expected_user
    result_mock = MagicMock()
    result_mock.scalars.return_value = scalars_mock
    db.execute = AsyncMock(return_value=result_mock)

    result = asyncio.run(UserCRUD.get_user_by_email(db, email="angel@test.com"))

    assert result == expected_user
    db.execute.assert_awaited_once()
    result_mock.scalars.assert_called_once()
    scalars_mock.first.assert_called_once()


def test_get_user_by_email_returns_none_when_not_found():
    db = MagicMock()
    scalars_mock = MagicMock()
    scalars_mock.first.return_value = None
    result_mock = MagicMock()
    result_mock.scalars.return_value = scalars_mock
    db.execute = AsyncMock(return_value=result_mock)

    result = asyncio.run(UserCRUD.get_user_by_email(db, email="missing@test.com"))

    assert result is None
    db.execute.assert_awaited_once()
    result_mock.scalars.assert_called_once()
    scalars_mock.first.assert_called_once()


def test_create_user_adds_commits_and_refreshes(monkeypatch):
    db = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    class FakeUser:
        def __init__(self, email: str, password: str):
            self.email = email
            self.password = password

    monkeypatch.setattr(user_crud_module, "User", FakeUser)

    payload = UserCreate(email="angel@test.com", password="Strong@123")
    result = asyncio.run(UserCRUD.create_user(db, payload))

    assert isinstance(result, FakeUser)
    assert result.email == "angel@test.com"
    assert result.password == "Strong@123"
    db.add.assert_called_once_with(result)
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(result)
