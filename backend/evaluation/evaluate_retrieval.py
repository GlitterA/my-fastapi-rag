import json
from pathlib import Path
import os
from app.rag.vectorstore import init_vector_store
from app.rag.retriever import build_bm25_retriever, reciprocal_rank_fusion

# 改变启动目录
os.chdir(Path(__file__).resolve().parent.parent)

QUERY_FILE = Path(__file__).parent / "queries.json"


def load_queries():
    with open(QUERY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def is_relevant(doc, query):
    """
    判断 Document 是否命中 Ground Truth
    """

    source = Path(doc.metadata.get("source", "")).name
    page = int(doc.metadata.get("page_label"))

    # 新格式：多个 source
    if "ground_truth" in query:
        for target in query["ground_truth"]:
            target_source = Path(target["source"]).name
            target_pages = target["pages"]

            if (
                    source == target_source
                    and page in target_pages
            ):
                return True

        return False

    # 兼容原来的单 source 格式
    target_source = Path(query["source"]).name
    target_pages = query["pages"]

    return (
            source == target_source
            and page in target_pages
    )


def metrix():
    queries = load_queries()

    vector_store = init_vector_store()
    for query in queries:
        question = query["question"]

        docs = vector_store.similarity_search(
            question,
            k=5
        )

        print("\n" + "=" * 80)
        print(query["id"])
        print("Question:", question)

        print("\nGround Truth:")
        print("source:", query["source"])
        print("pages:", query["pages"])

        print("\nRetrieved:")

        for i, doc in enumerate(docs, 1):
            print(f"\nTop {i}")
            print("source:", doc.metadata.get("source"))
            print("page:", doc.metadata.get("page"))
            print("page_label:", doc.metadata.get("page_label"))
            print("content:", doc.page_content[:200])


def single_query_metrix():
    from app.rag.vectorstore import init_vector_store
    queries = load_queries()
    vector_store = init_vector_store()

    for query in queries:
        if query["id"] != "Q001":
            continue

        question = query["question"]
        docs_with_scores = vector_store.similarity_search_with_score(question, k=5)

        print("\n" + "=" * 100)
        print(query["id"])
        print("Question:", question)

        # Ground Truth
        print("\nGround Truth:")
        if "ground_truth" in query:
            for target in query["ground_truth"]:
                print(f"  source={target['source']}, pages={target['pages']}")
        else:
            print(f"  source={query['source']}, pages={query['pages']}")

        # Retrieved Results
        print("\nTop 5 Retrieved:")
        for i, (doc, score) in enumerate(docs_with_scores, 1):
            print(f"\nTop {i}")
            print("score:", score)
            print("source:", doc.metadata.get("source"))
            print("page:", doc.metadata.get("page"))
            print("page_label:", doc.metadata.get("page_label"))
            print("content:", doc.page_content[:500])


def rrf_evl():
    queries = load_queries()

    vector_store = init_vector_store()
    vector_retriever = vector_store.as_retriever(
        search_kwargs={"k": 5}
    )
    bm25 = build_bm25_retriever(vector_store)

    results = {
        "vector": [],
        "bm25": [],
        "rrf": [],
    }

    for query in queries:
        question = query["question"]

        vector_docs = vector_retriever.invoke(question)
        bm25_docs = bm25.invoke(question)

        rrf_docs = reciprocal_rank_fusion(
            [vector_docs, bm25_docs], [0.99, 0.01]
        )[:5]

        retrieval_results = {
            "vector": vector_docs,
            "bm25": bm25_docs,
            "rrf": rrf_docs,
        }

        for name, docs in retrieval_results.items():

            hit_at = []

            for k in [1, 3, 5]:
                hit = any(
                    is_relevant(doc, query)
                    for doc in docs[:k]
                )
                hit_at.append(hit)

            result = {
                "id": query["id"],
                "question": question,
                "hit@1": hit_at[0],
                "hit@3": hit_at[1],
                "hit@5": hit_at[2],
            }

            results[name].append(result)

            print(
                f"{query['id']} | "
                f"{name:<6} "
                f"@1={hit_at[0]} "
                f"@3={hit_at[1]} "
                f"@5={hit_at[2]}"
            )

    # 汇总结果
    print("\n========== Evaluation Result ==========")

    for name, method_results in results.items():

        print(f"\n[{name.upper()}]")

        total = len(method_results)

        for k in [1, 3, 5]:
            recall = sum(
                result[f"hit@{k}"]
                for result in method_results
            ) / total

            print(
                f"Recall@{k}: "
                f"{recall:.2%}"
            )


if __name__ == "__main__":
    # 检索器召回评估（vector / bm25 / rrf 三方法 Recall@1/3/5）
    rrf_evl()
