from pydantic import BaseModel, ConfigDict

from schemas.project_schema import Project


class UserProjectBase(BaseModel):
    user_id: int
    project_id: int
    is_owner: bool = False


class UserProjectCreate(UserProjectBase):
    pass


class UserProjectWithProject(BaseModel):
    is_owner: bool
    project: Project

    model_config = ConfigDict(from_attributes=True)
