from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services import Base

if TYPE_CHECKING:
    from models.document_model import Document
    from models.user_project_model import UserProject


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    documents: Mapped[list["Document"]] = relationship(
        back_populates="project", cascade="all, delete"
    )
    users_access: Mapped[list["UserProject"]] = relationship(
        back_populates="project", cascade="all, delete"
    )
