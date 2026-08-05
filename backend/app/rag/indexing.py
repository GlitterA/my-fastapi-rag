from langchain_core.documents import Document
from app.api.routes.qa import vector_store


def init_vector_store():
    docs = [
        Document(
            page_content="小明最喜欢的数字是888",
            metadata={
                "source": "test"
            }
        ),
        Document(
            page_content="小明最喜欢的水果是苹果",
            metadata={
                "source": "test"
            }
        )
    ]

    vector_store.add_documents(docs)
