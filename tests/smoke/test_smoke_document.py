from pytest import fixture
import io

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
def uploaded_document_id(user_1_client):
    response = user_1_client.post(
        "/projects",
        json={"name": "Super project", "description": "A super project"},
    )
    assert response.is_success
    project_id = response.json()["message"].split("ID: ")[1]

    response_doc = user_1_client.post(
        f"/project/{project_id}/documents",
        files={"file": ("document_1.pdf", io.BytesIO(PDF_CONTENT), "application/pdf")},
    )
    assert response_doc.is_success
    return response_doc.json()["id"]


def test_get_document_success(user_1_client, uploaded_document_id):
    response = user_1_client.get(f"/document/{uploaded_document_id}")

    assert response.is_success
    assert response.json()["id"] == uploaded_document_id


def test_get_document_not_found(user_1_client):
    response = user_1_client.get("/document/9999")

    assert response.status_code == 404


def test_update_document_success(user_1_client, uploaded_document_id):
    new_pdf_content = (
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

    response = user_1_client.put(
        f"/document/{uploaded_document_id}",
        files={
            "file": (
                "updated_document.pdf",
                io.BytesIO(new_pdf_content),
                "application/pdf",
            )
        },
    )

    assert response.is_success
    assert response.json()["name"] == "updated_document.pdf"


def test_update_document_not_found(user_1_client):
    new_pdf_content = (
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

    response = user_1_client.put(
        "/document/9999",
        files={
            "file": (
                "updated_document.pdf",
                io.BytesIO(new_pdf_content),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 404


def test_delete_document_success(user_1_client, uploaded_document_id):
    response = user_1_client.delete(f"/document/{uploaded_document_id}")

    assert response.is_success

    response_get = user_1_client.get(f"/document/{uploaded_document_id}")
    assert response_get.status_code == 404


def test_delete_document_not_found(user_3_client, uploaded_document_id):
    response = user_3_client.delete(f"/document/{uploaded_document_id}")

    assert response.status_code == 404


def test_delete_document_not_found_2(user_1_client):
    response = user_1_client.delete("/document/999")

    assert response.status_code == 404


def test_delete_document_not_owner(user_1_client, user_2_info, user_2_client):
    """Test that delete document endpoint works with valid credentials and project not found"""
    response = user_1_client.post(
        "/projects",
        json={"name": "Super project", "description": "A super project"},
    )
    assert response.is_success
    project_id = response.json()["message"].split("ID: ")[1]

    response_doc = user_1_client.post(
        f"/project/{project_id}/documents",
        files={"file": ("document_1.pdf", io.BytesIO(PDF_CONTENT), "application/pdf")},
    )
    assert response_doc.is_success
    uploaded_document_id = response_doc.json()["id"]

    response_2 = user_1_client.post(
        f"/project/{project_id}/invite",
        params={"user_email": user_2_info["email"]},
    )

    assert response_2.is_success

    response_3 = user_2_client.delete(f"/document/{uploaded_document_id}")

    assert response_3.status_code == 404
