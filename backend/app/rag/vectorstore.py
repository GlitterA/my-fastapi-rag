# 负责初始化向量数据库

from app.core.settings import settings
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings


def init_vector_store():
    embeddings = DashScopeEmbeddings(
        model="qwen3.7-text-embedding",
        dashscope_api_key=settings.DASHSCOPE_API_KEY
    )

    vector_store = Chroma(
        collection_name="test",
        embedding_function=embeddings,
        persist_directory="./data/chroma"
    )

    return vector_store
