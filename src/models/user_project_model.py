from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services import DatabaseConnection

if TYPE_CHECKING:
    from models.project_model import Project
    from models.user_model import User


class UserProject(DatabaseConnection().get_base()):
    __tablename__ = "users_projects"
    user_email: Mapped[str] = mapped_column(
        ForeignKey("users.email"), primary_key=True, nullable=False
    )
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"), primary_key=True, nullable=False
    )
    is_owner: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    user: Mapped["User"] = relationship(back_populates="projects_access")
    project: Mapped["Project"] = relationship(back_populates="users_access")
