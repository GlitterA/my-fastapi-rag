from langchain_core.language_models import LanguageModelLike
from langchain_core.retrievers import BaseRetriever
from langchain_core.prompts import BasePromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.runnables import RunnableBranch, RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from loguru import logger

def build_history_aware_retriever(
        llm: LanguageModelLike,
        retriever: BaseRetriever,
        prompt: BasePromptTemplate
) -> Runnable[dict, list[Document]]:
    """
    Runnable
    传入类型形如：
    {
        ”input“: str
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
) -> Runnable[dict, str]:
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
            ) | document_chain
    )
