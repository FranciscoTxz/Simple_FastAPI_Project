import asyncio
from hashlib import sha1
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

import services.user_service as user_service_module
from schemas.user_schema import UserCreate
from services.user_service import UserService


def _make_payload(
    email: str = "angel@test.com", password: str = "Strong@123"
) -> UserCreate:
    return UserCreate(email=email, password=password)


# ---------------------------------------------------------------------------
# signup_user
# ---------------------------------------------------------------------------


def test_signup_raises_400_when_email_already_registered(monkeypatch):
    db = MagicMock()
    monkeypatch.setattr(
        user_service_module.UserCRUD,
        "get_user_by_email",
        AsyncMock(return_value=SimpleNamespace(email="angel@test.com")),
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(UserService.signup_user(user=_make_payload(), db=db))

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Email already registered"


def test_signup_hashes_password_and_creates_user(monkeypatch):
    db = MagicMock()
    create_mock = AsyncMock(return_value=None)
    monkeypatch.setattr(
        user_service_module.UserCRUD, "get_user_by_email", AsyncMock(return_value=None)
    )
    monkeypatch.setattr(user_service_module.UserCRUD, "create_user", create_mock)

    result = asyncio.run(UserService.signup_user(user=_make_payload(), db=db))

    assert result == {"message": "User created successfully"}
    called_user = create_mock.call_args[0][1]
    assert called_user.password == sha1("Strong@123".encode()).hexdigest()


# ---------------------------------------------------------------------------
# login_user
# ---------------------------------------------------------------------------


def test_login_raises_400_when_user_not_found(monkeypatch):
    db = MagicMock()
    response = MagicMock()
    monkeypatch.setattr(
        user_service_module.UserCRUD, "get_user_by_email", AsyncMock(return_value=None)
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            UserService.login_user(user=_make_payload(), response=response, db=db)
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid email or password"


def test_login_raises_400_when_password_is_wrong(monkeypatch):
    db = MagicMock()
    response = MagicMock()
    stored_hash = sha1("OtherPassword@1".encode()).hexdigest()
    monkeypatch.setattr(
        user_service_module.UserCRUD,
        "get_user_by_email",
        AsyncMock(
            return_value=SimpleNamespace(email="angel@test.com", password=stored_hash)
        ),
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            UserService.login_user(
                user=_make_payload(password="Strong@123"), response=response, db=db
            )
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid email or password"


def test_login_sets_cookie_header_and_returns_token(monkeypatch):
    db = MagicMock()
    response = MagicMock()
    stored_hash = sha1("Strong@123".encode()).hexdigest()
    fake_token = "fake.jwt.token"
    monkeypatch.setattr(
        user_service_module.UserCRUD,
        "get_user_by_email",
        AsyncMock(
            return_value=SimpleNamespace(email="angel@test.com", password=stored_hash)
        ),
    )
    monkeypatch.setattr(
        user_service_module.jwt, "encode", lambda *args, **kwargs: fake_token
    )

    result = asyncio.run(
        UserService.login_user(user=_make_payload(), response=response, db=db)
    )

    assert result["message"] == "Login successful"
    assert result["access_token"] == fake_token
    response.set_cookie.assert_called_once_with(
        key="AsyncSession_token",
        value=fake_token,
        httponly=True,
        max_age=3600,
    )
    response.headers.__setitem__.assert_called_once_with(
        "Authorization", f"Bearer {fake_token}"
    )
