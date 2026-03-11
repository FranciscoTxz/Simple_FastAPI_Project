from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services import Base

if TYPE_CHECKING:
    from models.user_project_model import UserProject


class User(Base):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(
        String, primary_key=True, index=True, nullable=False
    )
    password: Mapped[str] = mapped_column(String, nullable=False)
    projects_access: Mapped[list["UserProject"]] = relationship(back_populates="user")
