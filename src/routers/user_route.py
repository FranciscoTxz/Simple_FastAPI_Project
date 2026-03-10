from services import DatabaseConnection
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user_schema import UserCreate, SignUp, Login
from services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["users"])


@router.post("/signup", response_model=SignUp, status_code=201)
async def signup_user(
    user: UserCreate, db: AsyncSession = Depends(DatabaseConnection().get_session)
):
    return await UserService.signup_user(user, db)


@router.post("/login", response_model=Login)
async def login_user(
    user: UserCreate,
    response: Response,
    db: AsyncSession = Depends(DatabaseConnection().get_session),
):
    return await UserService.login_user(user, response, db)
