# 负责初始化向量数据库

from app.core.settings import settings
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings


def init_vector_store():
    if settings.ENVIRONMENT == "test":
        persist_directory = "./data/test_chroma"
    else:
        persist_directory = "./data/chroma"

    embeddings = DashScopeEmbeddings(
        model="qwen3.7-text-embedding",
        dashscope_api_key=settings.DASHSCOPE_API_KEY
    )
    vector_store = Chroma(
        collection_name="test",
        embedding_function=embeddings,
        persist_directory=persist_directory
    )
    return vector_store


def is_empty(vector_store):
    return vector_store._collection.count() == 0
