import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from commons import authentication as auth


def test_authentication_user_accepts_bearer_token(monkeypatch):
    db = MagicMock()
    expected_user = {"id": 1, "email": "angel@test.com"}
    decode_mock = MagicMock(return_value={"email": "angel@test.com"})
    get_user_mock = AsyncMock(return_value=expected_user)

    monkeypatch.setattr(auth.jwt, "decode", decode_mock)
    monkeypatch.setattr(auth.UserCRUD, "get_user_by_email", get_user_mock)

    result = asyncio.run(
        auth.authentication_user(
            authorization="Bearer token123",
            db=db,
        )
    )

    assert result == expected_user
    decode_mock.assert_called_once_with(
        "token123", auth.SECRET_KEY, algorithms=["HS256"]
    )
    get_user_mock.assert_awaited_once_with(db, "angel@test.com")


def test_authentication_user_accepts_non_bearer_authorization(monkeypatch):
    db = MagicMock()
    expected_user = {"id": 2, "email": "raw@test.com"}
    decode_mock = MagicMock(return_value={"email": "raw@test.com"})
    get_user_mock = AsyncMock(return_value=expected_user)

    monkeypatch.setattr(auth.jwt, "decode", decode_mock)
    monkeypatch.setattr(auth.UserCRUD, "get_user_by_email", get_user_mock)

    result = asyncio.run(
        auth.authentication_user(
            authorization="Token raw-token-value",
            db=db,
        )
    )

    assert result == expected_user
    decode_mock.assert_called_once_with(
        "Token raw-token-value", auth.SECRET_KEY, algorithms=["HS256"]
    )
    get_user_mock.assert_awaited_once_with(db, "raw@test.com")


def test_authentication_user_uses_session_cookie_when_header_missing(monkeypatch):
    db = MagicMock()
    expected_user = {"id": 3, "email": "cookie@test.com"}
    decode_mock = MagicMock(return_value={"email": "cookie@test.com"})
    get_user_mock = AsyncMock(return_value=expected_user)

    monkeypatch.setattr(auth.jwt, "decode", decode_mock)
    monkeypatch.setattr(auth.UserCRUD, "get_user_by_email", get_user_mock)

    result = asyncio.run(
        auth.authentication_user(
            session_token="cookie-token",
            authorization=None,
            db=db,
        )
    )

    assert result == expected_user
    decode_mock.assert_called_once_with(
        "cookie-token", auth.SECRET_KEY, algorithms=["HS256"]
    )
    get_user_mock.assert_awaited_once_with(db, "cookie@test.com")


def test_authentication_user_rejects_when_token_missing():
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            auth.authentication_user(
                session_token=None,
                authorization=None,
                db=MagicMock(),
            )
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Unauthorized: Missing or invalid token"


def test_authentication_user_rejects_expired_jwt(monkeypatch):
    monkeypatch.setattr(
        auth.jwt,
        "decode",
        MagicMock(side_effect=auth.jwt.ExpiredSignatureError("token expired")),
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            auth.authentication_user(
                authorization="Bearer token123",
                db=MagicMock(),
            )
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Unauthorized: Token has expired"


def test_authentication_user_rejects_invalid_jwt(monkeypatch):
    monkeypatch.setattr(
        auth.jwt,
        "decode",
        MagicMock(side_effect=auth.jwt.InvalidTokenError("invalid token")),
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            auth.authentication_user(
                authorization="Bearer token123",
                db=MagicMock(),
            )
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Unauthorized: Missing or invalid token"


def test_authentication_user_rejects_unexpected_exception(monkeypatch):
    monkeypatch.setattr(
        auth.jwt,
        "decode",
        MagicMock(side_effect=Exception("unexpected error")),
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            auth.authentication_user(
                authorization="Bearer token123",
                db=MagicMock(),
            )
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Unauthorized: Missing or invalid token"


def test_authentication_user_rejects_payload_without_email(monkeypatch):
    monkeypatch.setattr(auth.jwt, "decode", MagicMock(return_value={}))

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            auth.authentication_user(
                authorization="Bearer token123",
                db=MagicMock(),
            )
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Unauthorized: Missing or invalid token"


def test_authentication_user_rejects_when_user_not_found(monkeypatch):
    db = MagicMock()
    monkeypatch.setattr(
        auth.jwt,
        "decode",
        MagicMock(return_value={"email": "missing@test.com"}),
    )
    get_user_mock = AsyncMock(return_value=None)
    monkeypatch.setattr(auth.UserCRUD, "get_user_by_email", get_user_mock)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            auth.authentication_user(
                authorization="Bearer token123",
                db=db,
            )
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Unauthorized: User not found"
    get_user_mock.assert_awaited_once_with(db, "missing@test.com")
