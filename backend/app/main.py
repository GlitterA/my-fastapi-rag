from fastapi import FastAPI
from app.api.main import api_router
from contextlib import asynccontextmanager
from app.rag.indexing import init_vector_store
from loguru import logger

@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info(f"数据库初始化")
    init_vector_store()

    yield

app = FastAPI(
    lifespan=lifespan
)

@app.get("/")
def root():
    return {
        "message": "Welcome to root page"
    }


app.include_router(api_router)
