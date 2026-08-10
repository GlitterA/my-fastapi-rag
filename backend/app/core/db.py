# app/core/db.py
from sqlmodel import SQLModel, create_engine
from sqlalchemy.pool import StaticPool

# SQLite 数据库文件路径
SQLITE_URL = "sqlite:///./data/SQLite/app.db"

# 创建 engine（数据库连接池）
engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},  # FastAPI 必须
    poolclass=StaticPool,  # 单线程安全（开发很友好）
)


def create_db_and_tables():
    """启动时调用：建表"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """依赖注入用：获取数据库会话"""
    from sqlmodel import Session
    with Session(engine) as session:
        yield session
