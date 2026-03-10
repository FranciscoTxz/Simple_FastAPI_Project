import jwt
from fastapi import Cookie, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from commons.constants import SECRET_KEY
from crud.user_crud import UserCRUD
from services import DatabaseConnection


async def authentication_user(
    session_token: str | None = Cookie(default=None, alias="AsyncSession_token"),
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(DatabaseConnection().get_session),
):
    token = None

    if authorization:
        scheme, _, param = authorization.partition(" ")
        if scheme.lower() == "bearer" and param:
            token = param
        else:
            token = authorization

    if not token and session_token:
        token = session_token

    if not token:
        raise HTTPException(
            status_code=401, detail="Unauthorized: Missing or invalid token"
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401, detail="Unauthorized: Missing or invalid token"
        )

    email = payload.get("email")
    if not email:
        raise HTTPException(
            status_code=401, detail="Unauthorized: Missing or invalid token"
        )
    user = await UserCRUD.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized: User not found")
    return user
