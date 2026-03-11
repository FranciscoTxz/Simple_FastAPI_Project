import io
import base64
from pytest import fixture

PDF_CONTENT = (
    b"%PDF-1.4\n"
    b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
    b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]>>endobj\n"
    b"xref\n0 4\n"
    b"0000000000 65535 f \n"
    b"0000000009 00000 n \n"
    b"0000000058 00000 n \n"
    b"0000000115 00000 n \n"
    b"trailer<</Size 4/Root 1 0 R>>\n"
    b"startxref\n196\n%%EOF\n"
)


@fixture
def created_project_id(user_1_client):
    """Fixture que crea un proyecto y devuelve su ID"""
    response = user_1_client.post(
        "/projects",
        json={"name": "Super project", "description": "A super project"},
    )
    assert response.is_success
    return response.json()["message"].split("ID: ")[1]


@fixture
def uploaded_project_document(user_1_client, created_project_id):
    """Fixture que crea un proyecto con un documento y devuelve ambos IDs"""
    response_doc = user_1_client.post(
        f"/project/{created_project_id}/documents",
        files={"file": ("document_1.pdf", io.BytesIO(PDF_CONTENT), "application/pdf")},
    )
    assert response_doc.is_success
    return {
        "project_id": created_project_id,
        "document_id": response_doc.json()["id"],
    }


def test_create_project_success(user_1_client):
    """Test that create project endpoint works with valid credentials"""

    response = user_1_client.post(
        "/projects",
        json={"name": "Super project", "description": "A super project"},
    )

    assert response.is_success
    assert "message" in response.json()


def test_get_projects_success(user_1_client):
    """Test that get projects endpoint works with valid credentials"""

    response = user_1_client.post(
        "/projects",
        json={"name": "Super project", "description": "A super project"},
    )

    assert response.is_success

    response_2 = user_1_client.post(
        "/projects",
        json={"name": "Super project 2", "description": "A super project"},
    )

    assert response_2.is_success

    response_3 = user_1_client.get("/projects")

    assert response_3.is_success
    assert isinstance(response_3.json(), list)


def test_get_projects_no_projects_found(user_1_client):
    """Test that get projects endpoint works with valid credentials and not found"""
    response = user_1_client.get("/projects")

    assert response.status_code == 404


def test_create_project_alrady_exists(user_1_client):
    """Test that create project endpoint already exists with valid credentials"""

    response = user_1_client.post(
        "/projects",
        json={"name": "Super project", "description": "A super project"},
    )

    assert response.is_success

    response_2 = user_1_client.post(
        "/projects",
        json={"name": "Super project", "description": "A super project"},
    )

    assert response_2.status_code == 400


def test_create_project_validation_error(user_1_client):
    """Test that create project endpoint validation error with valid credentials"""

    response = user_1_client.post(
        "/projects",
        json={
            "name": "Super project",
        },
    )

    assert response.status_code == 400

    response_2 = user_1_client.post(
        "/projects",
        json={"description": "A super project"},
    )

    assert response_2.status_code == 400


def test_get_project_info_success(user_1_client, created_project_id):
    """Test that get project info endpoint works with valid credentials"""
    name = "Super project"
    description = "A super project"

    response_2 = user_1_client.get(f"/project/{created_project_id}/info")

    assert response_2.is_success
    assert response_2.json()["name"] == name
    assert response_2.json()["description"] == description


def test_get_project_info_not_found(user_1_client):
    """Test that get project info endpoint works with valid credentials and not found"""

    response_2 = user_1_client.get("/project/1000/info")

    assert response_2.status_code == 404


def test_update_project_success(user_1_client, created_project_id):
    """Test that update project endpoint works with valid credentials"""
    new_name = "Super project updated"
    new_description = "A super project updated"

    response_2 = user_1_client.put(
        f"/project/{created_project_id}/info",
        json={"name": new_name, "description": new_description},
    )

    assert response_2.is_success
    assert response_2.json()["name"] == new_name
    assert response_2.json()["description"] == new_description


def test_update_project_from_another_user(
    user_1_client, user_2_client, user_2_info, created_project_id
):
    new_name = "Super project updated"
    new_description = "A super project updated"

    response_2 = user_1_client.post(
        f"/project/{created_project_id}/invite",
        params={"user_email": user_2_info["email"]},
    )

    assert response_2.is_success

    response = user_2_client.put(
        f"/project/{created_project_id}/info",
        json={"name": new_name, "description": new_description},
    )

    assert response.status_code == 404


def test_delete_project_success(user_1_client, created_project_id):
    """Test that delete project endpoint works with valid credentials"""
    response_2 = user_1_client.delete(f"/project/{created_project_id}")

    assert response_2.status_code == 204


def test_delete_project_not_found(user_1_client):
    """Test that delete project endpoint works with valid credentials and project not found"""
    response = user_1_client.delete("/project/1000")

    assert response.status_code == 404


def test_delete_project_not_owner(
    user_1_client, user_2_client, user_2_info, created_project_id
):
    """Test that delete project endpoint works with valid credentials and project not found"""
    response_2 = user_1_client.post(
        f"/project/{created_project_id}/invite",
        params={"user_email": user_2_info["email"]},
    )

    assert response_2.is_success

    response_3 = user_2_client.delete(f"/project/{created_project_id}")

    assert response_3.status_code == 404


def test_create_project_document_success(user_1_client, created_project_id):
    """Test that create project document endpoint works with valid credentials"""
    file_name = "document_1.pdf"
    response_2 = user_1_client.post(
        f"/project/{created_project_id}/documents",
        files={"file": (file_name, io.BytesIO(PDF_CONTENT), "application/pdf")},
    )

    assert response_2.is_success
    assert response_2.json()["name"] == file_name
    assert response_2.json()["content"] == base64.b64encode(PDF_CONTENT).decode()


def test_create_project_document_not_found(user_1_client):
    """Test that create project document endpoint works with valid credentials"""
    file_name = "document_1.pdf"
    response_2 = user_1_client.post(
        "/project/1000/documents",
        files={"file": (file_name, io.BytesIO(PDF_CONTENT), "application/pdf")},
    )

    assert response_2.status_code == 404


def test_get_project_documents_success(user_1_client, created_project_id):
    """Test that get project documents endpoint works with valid credentials"""
    file_name = "document_1.pdf"
    response_2 = user_1_client.post(
        f"/project/{created_project_id}/documents",
        files={"file": (file_name, io.BytesIO(PDF_CONTENT), "application/pdf")},
    )

    assert response_2.is_success

    response_3 = user_1_client.get(f"/project/{created_project_id}/documents")

    assert response_3.is_success
    assert isinstance(response_3.json(), list)


def test_get_project_documents_success_no_documents(user_1_client, created_project_id):
    """Test that get project documents endpoint works with valid credentials"""
    response_2 = user_1_client.get(f"/project/{created_project_id}/documents")

    assert response_2.status_code == 404


def test_get_project_documents_not_found(user_1_client):
    """Test that get project documents endpoint works with valid credentials and project not found"""

    response = user_1_client.get("/project/1000/documents")

    assert response.status_code == 404


def test_invite_user_to_project_success(user_1_client, user_2_info, created_project_id):
    """Test that invite user to project endpoint works with valid credentials"""
    response_2 = user_1_client.post(
        f"/project/{created_project_id}/invite",
        params={"user_email": user_2_info["email"]},
    )

    assert response_2.is_success


def test_invite_user_to_project_is_already_in_project(
    user_1_client, user_2_info, created_project_id
):
    """Test that invite user to project endpoint works with valid credentials"""
    response_2 = user_1_client.post(
        f"/project/{created_project_id}/invite",
        params={"user_email": user_2_info["email"]},
    )

    assert response_2.is_success

    response_3 = user_1_client.post(
        f"/project/{created_project_id}/invite",
        params={"user_email": user_2_info["email"]},
    )

    assert response_3.status_code == 400
    assert response_3.json()["message"] == "User is already a member of the project"


def test_invite_user_to_project_user_dont_exists(user_1_client, created_project_id):
    """Test that invite user to project endpoint works with valid credentials"""
    response_2 = user_1_client.post(
        f"/project/{created_project_id}/invite",
        params={"user_email": "non_existent_user@example.com"},
    )

    assert response_2.status_code == 404


def test_invite_user_to_project_dont_exists(user_1_client):
    """Test that invite user to project endpoint works with valid credentials"""

    response = user_1_client.post(
        "/project/1000/invite",
        params={"user_email": "non_existent_user@example.com"},
    )

    assert response.status_code == 404


def test_invite_user_to_project_not_owner(
    user_1_client, user_2_info, user_2_client, created_project_id
):
    """Test that invite user to project endpoint works with valid credentials"""
    response_2 = user_1_client.post(
        f"/project/{created_project_id}/invite",
        params={"user_email": user_2_info["email"]},
    )

    assert response_2.is_success

    response_3 = user_2_client.post(
        f"/project/{created_project_id}/invite",
        params={"user_email": "non_existent_user@example.com"},
    )

    assert response_3.status_code == 404
