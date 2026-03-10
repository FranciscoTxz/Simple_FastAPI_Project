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
        try:
            if not user.name or not user.password:
                raise HTTPException(
                    status_code=400, detail="Name and password are required"
                )
            db_user = await UserCRUD.get_user_by_name(db, name=user.name)
            if db_user:
                raise HTTPException(status_code=400, detail="Name already registered")
            user.password = sha1(user.password.encode()).hexdigest()
            await UserCRUD.create_user(db, user)
            return {"message": "User created successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to create user: {str(e)}"
            )

    @staticmethod
    async def login_user(user: UserCreate, response: Response, db: AsyncSession):
        try:
            if not user.name or not user.password:
                raise HTTPException(
                    status_code=400, detail="Name and password are required"
                )
            db_user = await UserCRUD.get_user_by_name(db, name=user.name)
            if db_user is None:
                raise HTTPException(status_code=404, detail="User not found")
            if db_user.password != sha1(user.password.encode()).hexdigest():
                raise HTTPException(status_code=400, detail="Incorrect password")
            # JWT token generation 1 hour expiration
            expire = datetime.now(timezone.utc) + timedelta(hours=1)
            token = jwt.encode(
                {"username": user.name, "user_id": db_user.id, "exp": expire},
                SECRET_KEY,
                algorithm="HS256",
            )
            response.set_cookie(
                key="AsyncSession_token", value=token, httponly=True, max_age=3600
            )
            response.headers["Authorization"] = f"Bearer {token}"
            return {"message": "Login successful", "access_token": token}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")
