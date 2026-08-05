from app.rag.documents import load_documents
from app.rag.splitter import get_text_splitter


if __name__ == "__main__":

    # 1. 测试文档加载
    documents = load_documents("./knowledge")

    print(f"加载文档数量: {len(documents)}")

    for i, doc in enumerate(documents[:3]):
        print("=" * 50)
        print(f"第{i}个Document")
        print("内容:")
        print(doc.page_content[:200])
        print("metadata:")
        print(doc.metadata)


    # 2. 测试切分
    splitter = get_text_splitter()

    chunks = splitter.split_documents(
        documents
    )

    print("=" * 50)
    print(f"切分后chunk数量: {len(chunks)}")


    for i, chunk in enumerate(chunks[:3]):
        print("=" * 50)
        print(f"chunk {i}")
        print(chunk.page_content[:200])
        print(chunk.metadata)