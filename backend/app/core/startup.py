from app.core.db import create_db_and_tables
from loguru import logger
from app.rag.vectorstore import init_vector_store, is_empty
from app.rag.ingest import ingest_files
from pathlib import Path
from app.rag.chains import get_conversational_rag_chain, get_context_retriever_chain
from app.rag.memory import ChatMemory
from fastapi import FastAPI

def init_database(app: FastAPI):
    logger.info("加载SQLite")
    create_db_and_tables()

    logger.info("加载向量数据库")

    vector_store = init_vector_store()
    if is_empty(vector_store):
        ingest_files(
            Path("./data/knowledge"),
            vector_store
        )

    app.state.vector_store = vector_store


def init_rag(app: FastAPI):
    logger.info("初始化langchain调用链")
    retriever_chain = get_context_retriever_chain(app.state.vector_store)
    rag_chain = get_conversational_rag_chain(retriever_chain)

    app.state.rag_chain = rag_chain


def init_memory(app: FastAPI):
    logger.info("初始化用户历史信息")
    app.state.chat_memory = ChatMemory()
