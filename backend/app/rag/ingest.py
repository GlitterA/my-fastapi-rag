# 负责文档的加载

from langchain_core.vectorstores import VectorStore
from app.rag.documents import load_documents
from app.rag.splitter import get_text_splitter


def ingest_documents(
        source_dir: str,
        vector_store: VectorStore,
        batch_size=20
):
    """
    加载文件并写入向量数据库

    source_dir:
        原始文档目录

    vector_store:
        向量数据库实例
    """

    # 加载文档
    documents = load_documents(source_dir)

    # 文档切分
    chunks = get_text_splitter().split_documents(documents)
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        # 写入向量库
        vector_store.add_documents(batch)
