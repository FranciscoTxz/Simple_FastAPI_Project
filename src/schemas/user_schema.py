from pydantic import BaseModel, Field, field_validator
from fastapi import HTTPException
import re

PASSWORD_WHITELIST = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])(?!.*[\s~\\])[a-zA-Z\d!@#$%^&*]+$"
)
PASSWORD_REJECT = "Password must contain uppercase letters, lowercase letters, numbers, and special characters !@#$%^&*."


class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=8, max_length=16)

    @field_validator("password")
    def password_must_have(cls, v: str):
        if not PASSWORD_WHITELIST.fullmatch(v):
            raise HTTPException(
                status_code=400,
                detail=PASSWORD_REJECT,
            )
        return v


class UserCreate(UserBase):
    pass


class SignUp(BaseModel):
    message: str


class Login(BaseModel):
    message: str
    access_token: str
