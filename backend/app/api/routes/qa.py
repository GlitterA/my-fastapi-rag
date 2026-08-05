import os.path
from typing import Any
import yaml
from app.rag.chains import build_history_aware_retriever, build_stuff_documents_chain, build_retrieval_chain
from fastapi import APIRouter
from app.core.logger import logger
from app.core.settings import settings
from app.schema.chat_schema import ChatBody
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.vectorstores import VectorStore
from langchain_core.runnables import Runnable
from langchain_core.documents import Document
from app.rag.loader import vector_store

route = APIRouter()

# 设置配置文件路径
config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config/chat.yaml")

# 读取配置文件
with open(config_path, "r", encoding="utf-8") as config_file:
    config: dict[str, Any] = yaml.safe_load(config_file)
chat_config = config.get("CHAT_CONFIG", {})

# 打印对话配置日志
logger.info(f"Chat config: {chat_config}")

# 对话历史加载
# TODO：从文件中导入
chat_history = [AIMessage(content="Hello, I am a bot. How can I help you?")]


def get_context_retriever_chain(vector_store: VectorStore) \
        -> Runnable[dict, list[Document]]:
    """
    获得具有历史感知能力的检索链条
    """
    # 打印日志
    logger.info("构建上下文检索链")
    # 指定语言模型
    llm = ChatOpenAI(
        model=chat_config["LLM_MODEL"],
        api_key=settings.DASHSCOPE_API_KEY,
        base_url=settings.DASHSCOPE_BASE_URL
    )
    # 指定检索器
    retriever = vector_store.as_retriever()
    # 指定prompt
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "根据聊天历史和用户最新问题，生成一个用于检索的搜索查询"
            ),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ]
    )
    # 构造链
    retriever_chain = build_history_aware_retriever(
        llm=llm, retriever=retriever, prompt=prompt
    )

    return retriever_chain


def get_conversational_rag_chain(retriever_chain: Runnable):
    logger.info("构建rag会话链")
    llm = ChatOpenAI(
        model=chat_config["LLM_MODEL"],
        api_key=settings.DASHSCOPE_API_KEY,
        base_url=settings.DASHSCOPE_BASE_URL
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "基于以下上下文回答用户问题：{context}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ]
    )

    stuff_documents_chain = build_stuff_documents_chain(llm, prompt)
    return build_retrieval_chain(retriever_chain, stuff_documents_chain)


@route.post("/test/chat")
async def chat_action(request: ChatBody):
    global chat_history

    retriever = vector_store.as_retriever()

    # 指定用户消息
    user_message = HumanMessage(content=request.message)

    # 构建链
    retriever_chain = get_context_retriever_chain(vector_store)
    conversation_rag_chain = get_conversational_rag_chain(retriever_chain)

    # 打印日志
    logger.info(f"User message: {user_message.content}")
    logger.info(f"Chat history: {chat_history}")
    logger.info(f"request.message：{request.message}")
    # 调用链
    response = conversation_rag_chain.invoke(
        {"chat_history": chat_history, "input": request.message}
    )

    # 更新历史
    chat_history.append(user_message)
    ai_message = AIMessage(content=response)
    chat_history.append(ai_message)

    return {"data": response}
