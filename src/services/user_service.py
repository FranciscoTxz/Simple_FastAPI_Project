from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Response
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user_schema import UserCreate
from crud.user_crud import UserCRUD
from hashlib import sha1
from commons.constants import SECRET_KEY


class UserService:
    @staticmethod
    async def signup_user(user: UserCreate, db: AsyncSession):
        if not user.email or not user.password:
            raise HTTPException(
                status_code=400, detail="Email and password are required"
            )
        db_user = await UserCRUD.get_user_by_email(db, email=user.email)
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        user.password = sha1(user.password.encode()).hexdigest()
        await UserCRUD.create_user(db, user)
        return {"message": "User created successfully"}

    @staticmethod
    async def login_user(user: UserCreate, response: Response, db: AsyncSession):
        if not user.email or not user.password:
            raise HTTPException(
                status_code=400, detail="Email and password are required"
            )
        db_user = await UserCRUD.get_user_by_email(db, email=user.email)
        if db_user is None:
            raise HTTPException(status_code=400, detail="Invalid email or password")
        if db_user.password != sha1(user.password.encode()).hexdigest():
            raise HTTPException(status_code=400, detail="Invalid email or password")
        # JWT token generation 1 hour expiration
        expire = datetime.now(timezone.utc) + timedelta(hours=1)
        token = jwt.encode(
            {"email": user.email, "exp": expire},
            SECRET_KEY,
            algorithm="HS256",
        )
        response.set_cookie(
            key="AsyncSession_token", value=token, httponly=True, max_age=3600
        )
        response.headers["Authorization"] = f"Bearer {token}"
        return {"message": "Login successful", "access_token": token}
