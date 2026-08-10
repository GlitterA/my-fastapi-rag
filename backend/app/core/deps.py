from fastapi import Request
from langchain_core.vectorstores import VectorStore
from langchain_core.runnables import Runnable
from app.rag.memory import ChatMemory


def get_vector_store(request: Request) -> VectorStore:
    return request.app.state.vector_store


def get_rag_chain(request: Request) -> Runnable:
    return request.app.state.rag_chain

def get_chat_memory(request: Request) -> ChatMemory:
    return request.app.state.chat_memory
