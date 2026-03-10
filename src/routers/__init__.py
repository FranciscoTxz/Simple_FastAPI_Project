from .user_route import router as user_r
from .project_route import router as project_r, router_project
from .project_route import router_project as project_r2
from .document_route import router as docuemnt_r

__all__ = ["user_r", "project_r", "docuemnt_r", "project_r2", "router_project"]
