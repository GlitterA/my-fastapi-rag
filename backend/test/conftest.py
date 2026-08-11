import pytest
import uuid
from fastapi.testclient import TestClient
import os
from pathlib import Path
import shutil
from app.core.db import get_engine
from sqlmodel import Session
from test.fake_rag import FakeRagChain

os.environ["ENVIRONMENT"] = "test"

# rag/memory.py中使用
os.environ["CHAT_HISTORY_DIR"] = "./data/test_chat_history"

# core/db.py中使用
os.environ["SQLITE_URL"] = "sqlite:///./data/SQLite/test.db"

# api/routes/documents.py中使用
os.environ["DOCUMENTS_DIR"] = "./data/test_knowledge"

TEST_DB = Path("./data/SQLite/test.db")
TEST_CHROMA = Path("./data/test_chroma")
TEST_DOCUMENT = Path("./data/test_knowledge")
TEST_CHAT = Path("./data/test_chat_history")


@pytest.fixture(
    scope="session",
    autouse=True
)
# 清理测试垃圾
def clean_test_data():
    paths = [
        TEST_DB,
        TEST_CHROMA,
        TEST_DOCUMENT,
        TEST_CHAT
    ]
    for path in paths:
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

    # 删除后重新创建需要作为目录使用的路径
    TEST_CHROMA.mkdir(parents=True, exist_ok=True)
    TEST_DOCUMENT.mkdir(parents=True, exist_ok=True)
    TEST_CHAT.mkdir(parents=True, exist_ok=True)

    yield


from app.main import app


@pytest.fixture
def client():
    """
    创建FastAPI测试客户端

    用于模拟HTTP请求
    """

    app.state.rag_chain = FakeRagChain()
    with TestClient(app) as c:
        yield c


@pytest.fixture
def app_instance():
    from app.main import app
    from app.rag.memory import ChatMemory

    app.state.chat_memory = ChatMemory()

    return app


@pytest.fixture
def session():
    engine = get_engine()
    with Session(engine) as session:
        yield session


@pytest.fixture
def test_username():
    """
    每次测试生成唯一用户名

    防止同一次pytest运行中不同测试互相影响
    """
    return f"pytest_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def auth_headers(client, test_username):
    """
    返回一个用户的JWT
    """
    return create_user_and_login(
        client,
        test_username
    )


@pytest.fixture
def another_user(client):
    """
    返回另一个用户的JWT
    """

    username = f"pytest_{uuid.uuid4().hex[:8]}"

    return create_user_and_login(
        client,
        username
    )


def create_user_and_login(client, test_username):
    """
    测试环境中快速创建一个用户并获取JWT
    """
    response = client.post(
        "/create",
        json={
            "username": test_username,
            "password": "123456"
        }
    )

    assert response.status_code == 200

    response = client.post(
        "/login/access-token",
        data={
            "username": test_username,
            "password": "123456"
        }
    )

    assert response.status_code == 200

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
