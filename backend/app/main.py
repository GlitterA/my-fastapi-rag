from fastapi import FastAPI
from app.api.main import api_router
from contextlib import asynccontextmanager
from app.rag.vectorstore import init_vector_store
from app.rag.ingest import ingest_documents
from loguru import logger

@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("初始化向量数据库")
    vector_store = init_vector_store()
    ingest_documents(
        "./knowledge",
        vector_store
    )
    app.state.vector_store = vector_store

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
