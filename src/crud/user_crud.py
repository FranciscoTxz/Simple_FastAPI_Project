from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.user_model import User
from schemas.user_schema import UserCreate


class UserCRUD:
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str):
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    @staticmethod
    async def create_user(db: AsyncSession, user: UserCreate):
        db_user = User(email=user.email, password=user.password)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
