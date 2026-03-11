import asyncio
import time
from collections.abc import Generator
from hashlib import sha1

import asyncpg
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from testcontainers.core.container import DockerContainer

from models.document_model import Document
from models.project_model import Project
from models.user_model import User
from models.user_project_model import UserProject

# Deletion order respects FK constraints: dependents first
TABLES = [UserProject, Document, Project]

USER_1_EMAIL = "fake1@hot.com"
USER_1_PASSWORD = "TestPass123!"

USER_2_EMAIL = "fake2@hot.com"
USER_2_PASSWORD = "SuperPass123!"

USER_3_EMAIL = "fake3@hot.com"
USER_3_PASSWORD = "MegaPass123!"

USERS_FIXTURE_DATA = [
    {"email": USER_1_EMAIL, "password": USER_1_PASSWORD},
    {"email": USER_2_EMAIL, "password": USER_2_PASSWORD},
    {"email": USER_3_EMAIL, "password": USER_3_PASSWORD},
]


@pytest.fixture(scope="session")
def user_1_info():
    return USERS_FIXTURE_DATA[0]


@pytest.fixture(scope="session")
def user_2_info():
    return USERS_FIXTURE_DATA[1]


@pytest.fixture(scope="session")
def user_3_info():
    return USERS_FIXTURE_DATA[2]


async def _ping_postgres(dsn: str) -> None:
    conn = await asyncpg.connect(dsn)
    await conn.close()


@pytest.fixture(scope="session")
def session_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.run_until_complete(asyncio.sleep(0))
    loop.close()


def wait_until_ready(
    loop: asyncio.AbstractEventLoop, host: str, port: int, timeout: float = 30
) -> None:
    dsn = f"postgresql://test:test@{host}:{port}/test"
    deadline = time.time() + timeout
    while True:
        try:
            loop.run_until_complete(_ping_postgres(dsn))
            return
        except Exception:
            if time.time() > deadline:
                raise
            time.sleep(0.5)


@pytest.fixture(scope="session")
def postgres_container(session_loop) -> Generator[str, None, None]:
    with (
        DockerContainer("postgres:16")
        .with_exposed_ports(5432)
        .with_env("POSTGRES_USER", "test")
        .with_env("POSTGRES_PASSWORD", "test")
        .with_env("POSTGRES_DB", "test") as container
    ):
        host = container.get_container_host_ip()
        port = container.get_exposed_port(5432)
        wait_until_ready(session_loop, host, port)
        yield f"postgresql+asyncpg://test:test@{host}:{port}/test"


@pytest.fixture(scope="session", autouse=True)
def setup_test_db(postgres_container, session_loop):
    from services import DatabaseConnection

    db = DatabaseConnection()
    test_engine = create_async_engine(postgres_container, poolclass=NullPool)
    test_session_factory = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )

    # Patch the singleton so the app uses the container DB
    db.engine = test_engine
    db.AsyncSessionLocal = test_session_factory

    async def create_tables():
        async with test_engine.begin() as conn:
            await conn.run_sync(db.Base.metadata.create_all)

    session_loop.run_until_complete(create_tables())

    yield

    async def cleanup():
        async with test_engine.begin() as conn:
            await conn.run_sync(db.Base.metadata.drop_all)
        await test_engine.dispose()

    session_loop.run_until_complete(cleanup())


@pytest.fixture(scope="session")
def create_fixed_tables(setup_test_db, session_loop):
    from services import DatabaseConnection

    db = DatabaseConnection()

    async def seed():
        async with db.AsyncSessionLocal() as session:
            for user_data in USERS_FIXTURE_DATA:
                password_hash = sha1(user_data["password"].encode()).hexdigest()
                session.add(User(email=user_data["email"], password=password_hash))
            await session.commit()

    session_loop.run_until_complete(seed())

    yield

    async def teardown():
        async with db.AsyncSessionLocal() as session:
            for model in TABLES:
                await session.execute(delete(model))
            await session.execute(delete(User))
            await session.commit()

    session_loop.run_until_complete(teardown())


@pytest.fixture(scope="function")
def db_session(create_fixed_tables, session_loop):
    from services import DatabaseConnection

    db = DatabaseConnection()

    async def clear():
        async with db.AsyncSessionLocal() as session:
            for model in TABLES:
                await session.execute(delete(model))
            await session.commit()

    session_loop.run_until_complete(clear())
    yield
    session_loop.run_until_complete(clear())


def _login_client(email: str, password: str) -> TestClient:
    from app import app

    client = TestClient(app)
    login_response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.json()}"
    token = login_response.json().get("access_token")
    client.headers.update({"authorization": f"{token}"})
    return client


@pytest.fixture(scope="function")
def user_1_client(db_session) -> TestClient:
    return _login_client(USER_1_EMAIL, USER_1_PASSWORD)


@pytest.fixture(scope="function")
def user_2_client(db_session) -> TestClient:
    return _login_client(USER_2_EMAIL, USER_2_PASSWORD)


@pytest.fixture(scope="function")
def user_3_client(db_session) -> TestClient:
    return _login_client(USER_3_EMAIL, USER_3_PASSWORD)
