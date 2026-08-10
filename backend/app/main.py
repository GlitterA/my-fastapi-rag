from fastapi import FastAPI
from app.api.main import api_router
from contextlib import asynccontextmanager
from loguru import logger
from app.core.startup import init_database, init_rag, init_memory
from app.core.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 初始化数据库
    init_database(app)
    # 初始化rag链
    if settings.ENVIRONMENT != "test":
        init_rag(app)
    # 初始化用户历史信息
    init_memory(app)
    yield

    logger.info("释放资源")


app = FastAPI(
    lifespan=lifespan
)


@app.get("/")
def root():
    return {
        "message": "Welcome to root page"
    }


app.include_router(api_router)
