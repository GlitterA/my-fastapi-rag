import pytest
import uuid
from fastapi.testclient import TestClient
import os

os.environ["SQLITE_URL"] = (
    "sqlite:///./data/SQLite/test.db"
)
os.environ["ENVIRONMENT"] = "test"
from app.main import app


@pytest.fixture
def client():
    """
    创建FastAPI测试客户端

    用于模拟HTTP请求
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture
def test_username():
    """
    每次测试生成唯一用户名

    避免污染真实数据库
    """
    return f"pytest_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def auth_headers(client, test_username):
    response = client.post(
        "/create",
        json={
            "username": test_username,
            "password": "123456"
        }
    )

    assert response.status_code == 200

    # 登录获取token
    response = client.post(
        "/login/access-token",
        data={
            "username": test_username,
            "password": "123456"
        }
    )
    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

    token = response.json()["access_token"]
    return {
        "headers": {
            "Authorization": f"Bearer {token}"
        },
        "username": test_username
    }


@pytest.fixture
def vector_store(client):
    """
    获取测试期间FastAPI初始化好的向量数据库
    """
    return app.state.vector_store
