from langchain_openai import OpenAIEmbeddings
from app.core.settings import settings
from langchain_chroma import Chroma
# 指定嵌入模型
# embeddings = OpenAIEmbeddings(
#     model="qwen3.7-text-embedding",
#     api_key=settings.DASHSCOPE_API_KEY,
#     base_url=settings.DASHSCOPE_BASE_URL
# )

from langchain_community.embeddings import DashScopeEmbeddings


embeddings = DashScopeEmbeddings(
    model="qwen3.7-text-embedding",
    dashscope_api_key=settings.DASHSCOPE_API_KEY
)
# 指定数据库
vector_store = Chroma(
    collection_name="test",
    embedding_function=embeddings
)