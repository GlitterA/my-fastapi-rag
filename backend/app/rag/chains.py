from langchain_openai.chat_models import ChatOpenAI
from app.core.settings import settings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.language_models import LanguageModelLike
from langchain_core.retrievers import BaseRetriever
from langchain_core.prompts import BasePromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.runnables import RunnableBranch, RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from loguru import logger
from langchain_core.vectorstores import VectorStore
from app.config import configs

# 打印对话配置日志
logger.info(f"Chat config: {configs.chat}")

def build_history_aware_retriever(
        llm: LanguageModelLike,
        retriever: BaseRetriever,
        prompt: BasePromptTemplate
) -> Runnable[dict, list[Document]]:
    """
    Runnable
    传入类型形如：
    {
        "input": str
        "chat_history": str
        ...
    }
    输出类型：list[Document]
    """

    if "input" not in prompt.input_variables:
        raise ValueError("Expected input to be a prompt variable "
                         f"but got {prompt.input_variables}")
    contextualize_chain = (
            prompt
            | llm
            | StrOutputParser()
    )

    retrieve_documents = RunnableBranch(
        (
            lambda x: not x.get("chat_history"),
            RunnableLambda(lambda x: x["input"]) | retriever
        ),
        contextualize_chain | retriever
    ).with_config(run_name="chat_retriever_chain")

    return retrieve_documents


def build_stuff_documents_chain(
        llm: LanguageModelLike,
        prompt: BasePromptTemplate
) -> Runnable[dict, str]:
    """
    Runnable
    输入类型形如：
    {
        "context": list[Document]
        "input": str
        ...
    }
    输出类型形如：
    str
    """
    if "context" not in prompt.input_variables:
        raise ValueError(
            "Prompt must contain context variable"
        )

    return (
            RunnablePassthrough.assign(
                context=lambda x: "\n\n".join(doc.page_content
                                              for doc in x["context"]
                                              )
            ) | prompt | llm | StrOutputParser()
    )


def build_retrieval_chain(
        retriever: Runnable,
        document_chain: Runnable
) -> Runnable[dict, dict]:
    """
    Runnable
    输入类型：
    retriever的输入类型
    输出类型
    document_chain的输出类型
    """
    return (
            RunnablePassthrough.assign(
                context=retriever
            )
            .assign(
                answer=document_chain
            )
    )

def get_context_retriever_chain(vector_store: VectorStore) \
        -> Runnable[dict, list[Document]]:
    """
    获得具有历史感知能力的检索链条
    """
    # 打印日志
    logger.info("构建上下文检索链")
    # 指定语言模型
    llm = ChatOpenAI(
        model=configs.chat.llm_model,
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
        model=configs.chat.llm_model,
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
