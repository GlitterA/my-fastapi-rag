from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain_core.vectorstores import VectorStore
import jieba


def chinese_tokenizer(text: str) -> list[str]:
    return list(jieba.cut(text))


def build_bm25_retriever(
        vector_store: VectorStore,
        k: int = 5,
) -> BM25Retriever:
    """
    根据现有向量库中的全部 Document 构建 BM25 检索器。
    """
    data = vector_store.get()

    documents = [
        Document(
            page_content=content,
            metadata=metadata,
        )
        for content, metadata in zip(
            data["documents"],
            data["metadatas"],
        )
    ]

    retriever = BM25Retriever.from_documents(
        documents,
        preprocess_func=chinese_tokenizer
    )

    retriever.k = k

    return retriever


def reciprocal_rank_fusion(
    result_lists: list[list[Document]],
    weights: list[float],
    k: int = 60,
) -> list[Document]:
    """
    使用 RRF 融合多个检索器的结果。

    result_lists:
        多个检索器返回的 Document 列表

    k:
        RRF 平滑参数
    """

    scores = {}
    documents = {}

    for results, weight in zip(result_lists, weights):
        for rank, doc in enumerate(results, start=1):
            doc_id = doc.metadata["chunk_id"]

            scores[doc_id] = (
                scores.get(doc_id, 0)
                + weight / (k + rank)
            )

            documents[doc_id] = doc

    ranked_ids = sorted(
        scores,
        key=scores.get,
        reverse=True,
    )

    return [documents[doc_id] for doc_id in ranked_ids]
