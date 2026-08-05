from fastapi import Request
from langchain_core.vectorstores import VectorStore


def get_vector_store(request: Request) -> VectorStore:
    return request.app.state.vector_store