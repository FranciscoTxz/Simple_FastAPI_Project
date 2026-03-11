import asyncio
import base64
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
from fastapi import HTTPException

from schemas.document_schema import FileSerializer
from schemas.project_schema import ProjectCreate, ProjectUpdate
from services.project_service import ProjectService

if TYPE_CHECKING:
    from models.user_model import User


def _make_user(email: str = "angel@test.com") -> "User":
    return cast("User", SimpleNamespace(email=email))


def _make_pdf_b64() -> str:
    return base64.b64encode(b"%PDF" + b"a" * 10).decode()


# ---------------------------------------------------------------------------
# get_projects
# ---------------------------------------------------------------------------


def test_get_projects_raises_404_when_no_projects_found():
    db = MagicMock()
    with patch(
        "services.project_service.UserProjectCRUD.get_user_projects",
        new=AsyncMock(return_value=[]),
    ):
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(ProjectService.get_projects(user=_make_user(), db=db))

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "No projects found for the user"


def test_get_projects_returns_projects_list():
    db = MagicMock()
    projects = [SimpleNamespace(id=1), SimpleNamespace(id=2)]
    with patch(
        "services.project_service.UserProjectCRUD.get_user_projects",
        new=AsyncMock(return_value=projects),
    ):
        result = asyncio.run(ProjectService.get_projects(user=_make_user(), db=db))

    assert result is projects


# ---------------------------------------------------------------------------
# create_project
# ---------------------------------------------------------------------------


def test_create_project_raises_400_when_name_already_exists():
    db = MagicMock()
    with patch(
        "services.project_service.ProjectCRUD.get_project_by_name",
        new=AsyncMock(return_value=SimpleNamespace(id=5, name="Existing")),
    ):
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(
                ProjectService.create_project(
                    project=ProjectCreate(name="Existing", description="Some desc"),
                    user=_make_user(),
                    db=db,
                )
            )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Project already exists"


def test_create_project_creates_project_and_returns_message():
    db = MagicMock()
    new_project = SimpleNamespace(id=10, name="New Project")
    create_user_project_mock = AsyncMock(return_value=None)
    with (
        patch(
            "services.project_service.ProjectCRUD.get_project_by_name",
            new=AsyncMock(return_value=None),
        ),
        patch(
            "services.project_service.ProjectCRUD.create_project",
            new=AsyncMock(return_value=new_project),
        ),
        patch(
            "services.project_service.UserProjectCRUD.create_user_project",
            new=create_user_project_mock,
        ),
    ):
        result = asyncio.run(
            ProjectService.create_project(
                project=ProjectCreate(name="New Project", description="A description"),
                user=_make_user(),
                db=db,
            )
        )

    assert "New Project" in result["message"]
    assert "angel@test.com" in result["message"]
    assert "10" in result["message"]
    create_user_project_mock.assert_awaited_once()


# ---------------------------------------------------------------------------
# get_project_info
# ---------------------------------------------------------------------------


def test_get_project_info_returns_project():
    db = MagicMock()
    project = SimpleNamespace(id=3, name="My Project")
    user_project = SimpleNamespace(is_owner=True, project=project)
    with patch(
        "services.project_service.UserProjectCRUD.is_project_from_user",
        new=AsyncMock(return_value=user_project),
    ):
        result = asyncio.run(
            ProjectService.get_project_info(project_id=3, user=_make_user(), db=db)
        )

    assert result is project


# ---------------------------------------------------------------------------
# update_project
# ---------------------------------------------------------------------------


def test_update_project_raises_404_when_user_is_not_owner():
    db = MagicMock()
    with patch(
        "services.project_service.UserProjectCRUD.is_project_from_user",
        new=AsyncMock(return_value=SimpleNamespace(is_owner=False)),
    ):
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(
                ProjectService.update_project(
                    project_id=5,
                    project=ProjectUpdate(
                        name="New name", description="New description"
                    ),
                    user=_make_user(),
                    db=db,
                )
            )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Project not found"


def test_update_project_returns_updated_project_when_owner():
    db = MagicMock()
    updated = SimpleNamespace(id=5, name="Updated", description="Updated desc")
    with (
        patch(
            "services.project_service.UserProjectCRUD.is_project_from_user",
            new=AsyncMock(return_value=SimpleNamespace(is_owner=True)),
        ),
        patch(
            "services.project_service.ProjectCRUD.update_project",
            new=AsyncMock(return_value=updated),
        ),
    ):
        result = asyncio.run(
            ProjectService.update_project(
                project_id=5,
                project=ProjectUpdate(name="Updated", description="Updated desc"),
                user=_make_user(),
                db=db,
            )
        )

    assert result is updated


# ---------------------------------------------------------------------------
# delete_project
# ---------------------------------------------------------------------------


def test_delete_project_raises_404_when_user_is_not_owner():
    db = MagicMock()
    with patch(
        "services.project_service.UserProjectCRUD.is_project_from_user",
        new=AsyncMock(return_value=SimpleNamespace(is_owner=False)),
    ):
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(
                ProjectService.delete_project(project_id=6, user=_make_user(), db=db)
            )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Project not found"


def test_delete_project_deletes_and_returns_none_when_owner():
    db = MagicMock()
    delete_mock = AsyncMock(return_value=None)
    with (
        patch(
            "services.project_service.UserProjectCRUD.is_project_from_user",
            new=AsyncMock(return_value=SimpleNamespace(is_owner=True)),
        ),
        patch(
            "services.project_service.ProjectCRUD.delete_project",
            new=delete_mock,
        ),
    ):
        result = asyncio.run(
            ProjectService.delete_project(project_id=6, user=_make_user(), db=db)
        )

    assert result is None
    delete_mock.assert_awaited_once_with(db, 6)


# ---------------------------------------------------------------------------
# get_project_documents
# ---------------------------------------------------------------------------


def test_get_project_documents_raises_404_when_no_documents():
    db = MagicMock()
    with (
        patch(
            "services.project_service.UserProjectCRUD.is_project_from_user",
            new=AsyncMock(return_value=SimpleNamespace(is_owner=True)),
        ),
        patch(
            "services.project_service.DocumentCRUD.get_documents_by_project",
            new=AsyncMock(return_value=[]),
        ),
    ):
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(
                ProjectService.get_project_documents(
                    project_id=7, user=_make_user(), db=db
                )
            )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "No documents found for project"


def test_get_project_documents_returns_documents():
    db = MagicMock()
    docs = [SimpleNamespace(id=1), SimpleNamespace(id=2)]
    with (
        patch(
            "services.project_service.UserProjectCRUD.is_project_from_user",
            new=AsyncMock(return_value=SimpleNamespace(is_owner=True)),
        ),
        patch(
            "services.project_service.DocumentCRUD.get_documents_by_project",
            new=AsyncMock(return_value=docs),
        ),
    ):
        result = asyncio.run(
            ProjectService.get_project_documents(project_id=7, user=_make_user(), db=db)
        )

    assert result is docs


# ---------------------------------------------------------------------------
# create_project_document
# ---------------------------------------------------------------------------


def test_create_project_document_returns_new_document():
    db = MagicMock()
    new_doc = SimpleNamespace(id=20, name="doc.pdf")
    file = FileSerializer(file_name="doc.pdf", file_content_base64=_make_pdf_b64())
    with (
        patch(
            "services.project_service.UserProjectCRUD.is_project_from_user",
            new=AsyncMock(return_value=SimpleNamespace(is_owner=True)),
        ),
        patch(
            "services.project_service.DocumentCRUD.create_document",
            new=AsyncMock(return_value=new_doc),
        ),
    ):
        result = asyncio.run(
            ProjectService.create_project_document(
                project_id=8, file=file, user=_make_user(), db=db
            )
        )

    assert result is new_doc


# ---------------------------------------------------------------------------
# invite_user_to_project
# ---------------------------------------------------------------------------


def test_invite_user_raises_404_when_requester_is_not_owner():
    db = MagicMock()
    with patch(
        "services.project_service.UserProjectCRUD.is_project_from_user",
        new=AsyncMock(return_value=SimpleNamespace(is_owner=False)),
    ):
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(
                ProjectService.invite_user_to_project(
                    project_id=9,
                    user_email="invite@test.com",
                    user=_make_user(),
                    db=db,
                )
            )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Project not found"


def test_invite_user_raises_404_when_invited_user_not_found():
    db = MagicMock()
    with (
        patch(
            "services.project_service.UserProjectCRUD.is_project_from_user",
            new=AsyncMock(return_value=SimpleNamespace(is_owner=True)),
        ),
        patch(
            "services.project_service.UserCRUD.get_user_by_email",
            new=AsyncMock(return_value=None),
        ),
    ):
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(
                ProjectService.invite_user_to_project(
                    project_id=9,
                    user_email="ghost@test.com",
                    user=_make_user(),
                    db=db,
                )
            )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User to invite not found"


def test_invite_user_raises_400_when_already_a_member():
    db = MagicMock()
    is_project_mock = AsyncMock(
        side_effect=[
            SimpleNamespace(is_owner=True),  # requester check
            SimpleNamespace(is_owner=False),  # invitee already exists
        ]
    )
    with (
        patch(
            "services.project_service.UserProjectCRUD.is_project_from_user",
            new=is_project_mock,
        ),
        patch(
            "services.project_service.UserCRUD.get_user_by_email",
            new=AsyncMock(return_value=SimpleNamespace(email="member@test.com")),
        ),
    ):
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(
                ProjectService.invite_user_to_project(
                    project_id=9,
                    user_email="member@test.com",
                    user=_make_user(),
                    db=db,
                )
            )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "User is already a member of the project"


def test_invite_user_succeeds_and_returns_message():
    db = MagicMock()
    create_mock = AsyncMock(return_value=None)
    is_project_mock = AsyncMock(
        side_effect=[
            SimpleNamespace(is_owner=True),  # requester check
            None,  # invitee not yet member
        ]
    )
    with (
        patch(
            "services.project_service.UserProjectCRUD.is_project_from_user",
            new=is_project_mock,
        ),
        patch(
            "services.project_service.UserCRUD.get_user_by_email",
            new=AsyncMock(return_value=SimpleNamespace(email="new@test.com")),
        ),
        patch(
            "services.project_service.UserProjectCRUD.create_user_project",
            new=create_mock,
        ),
    ):
        result = asyncio.run(
            ProjectService.invite_user_to_project(
                project_id=9,
                user_email="new@test.com",
                user=_make_user(),
                db=db,
            )
        )

    assert "new@test.com" in result["message"]
    assert "9" in result["message"]
    create_mock.assert_awaited_once()
