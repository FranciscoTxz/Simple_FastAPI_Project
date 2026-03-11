from fastapi.testclient import TestClient


def test_sign_up_success(db_session):
    """Test that sign-ip endpoint works with valid credentials"""
    from app import app

    client = TestClient(app)

    response = client.post(
        "/auth/signup",
        json={
            "email": "fake@patient.com",
            "password": "TestPass123!",
        },
    )

    assert response.is_success
    assert "message" in response.json()


def test_sign_up_validation_exception(db_session):
    """Test that sign-ip endpoint works with valid credentials"""
    from app import app

    client = TestClient(app)

    response = client.post(
        "/auth/signup",
        json={
            "password": "TestPass123!",
        },
    )

    assert response.status_code == 400

    response_2 = client.post(
        "/auth/signup",
        json={
            "email": "fake@hot.com",
        },
    )

    assert response_2.status_code == 400


def test_login_success(db_session, user_1_info):
    """Test that login endpoint works with valid credentials"""
    from app import app

    client = TestClient(app)

    response = client.post(
        "/auth/login",
        json={
            "email": user_1_info["email"],
            "password": user_1_info["password"],
        },
    )

    assert response.is_success
    assert "access_token" in response.json()


def test_signup_user_already_exist(db_session, user_1_info):
    """Test that signup endpoint works with valid credentials"""
    from app import app

    client = TestClient(app)

    response = client.post(
        "/auth/signup",
        json={
            "email": user_1_info["email"],
            "password": user_1_info["password"],
        },
    )

    assert response.status_code == 400


def test_login_user_dont_exist(db_session):
    """Test that login endpoint works with valid credentials"""
    from app import app

    client = TestClient(app)

    response = client.post(
        "/auth/login",
        json={
            "email": "nonexistent@user.com",
            "password": "SomePassword123!",
        },
    )

    assert response.status_code == 400


def test_login_user_incorrect_password(db_session, user_1_info):
    """Test that login endpoint works with valid credentials"""
    from app import app

    client = TestClient(app)

    response = client.post(
        "/auth/login",
        json={
            "email": user_1_info["email"],
            "password": "SomePassword123!",
        },
    )

    assert response.status_code == 400
