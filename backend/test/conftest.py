import pytest
from httpx import AsyncClient, ASGITransport
from sqlmodel import SQLModel, create_engine, Session
from app.main import app
from app.core.db import get_session

# 用内存 SQLite 替代真实数据库
TEST_DB_URL = "sqlite:///:memory:"

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    # 用测试 session 覆盖依赖
    def override_get_session():
        yield session

@pytest.fixture
def base_url():
    return "localhost:8000"

    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()