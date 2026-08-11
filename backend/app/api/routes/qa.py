from fastapi import APIRouter, Depends
from loguru import logger
from app.schema.chat_schema import ChatBody
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import Runnable
from app.core.deps import get_rag_chain, get_chat_memory, get_current_user
from fastapi.responses import StreamingResponse
from app.rag.memory import ChatMemory
import json
from app.model.user_model import User

route = APIRouter()


@route.post("/test/stream_chat")
async def stream_chat_action(
        request: ChatBody,
        current_user: User = Depends(get_current_user),
        memory: ChatMemory = Depends(get_chat_memory),
        rag_chain: Runnable = Depends(get_rag_chain)
):

    chat_history = memory.get_history(current_user.username)

    logger.info(f"User message: {request.message}")
    logger.info(f"Chat history: {chat_history}")

    async def generate():
        full_response = ""
        references = []

        try:
            async for chunk in rag_chain.astream({
                "chat_history": chat_history,
                "input": request.message
            }):
                # 正文流式输出
                if "answer" in chunk:
                    text = chunk["answer"]
                    full_response += text
                    yield json.dumps(
                        {"type": "token", "data": text},
                        ensure_ascii=False
                    ) + "\n"

                # 收集来源
                if "context" in chunk:
                    for doc in chunk["context"]:
                        references.append({
                            "source": doc.metadata.get("source"),
                            "content": doc.page_content
                        })

        except Exception:
            logger.exception("RAG生成失败")
            yield json.dumps(
                {"type": "error", "data": "系统错误"},
                ensure_ascii=False
            ) + "\n"

        finally:
            # 流结束后发送来源
            if full_response and not full_response.endswith("系统错误"):
                yield json.dumps(
                    {"type": "sources", "data": references},
                    ensure_ascii=False
                ) + "\n"

                memory.add_message(
                    current_user.username,
                    HumanMessage(content=request.message)
                )
                memory.add_message(
                    current_user.username,
                    AIMessage(content=full_response)
                )

    return StreamingResponse(
        generate(),
        media_type="application/x-ndjson"
    )


@route.post("/test/chat")
def chat_action(
        request: ChatBody,
        current_user: User = Depends(get_current_user),
        memory: ChatMemory = Depends(get_chat_memory),
        rag_chain: Runnable = Depends(get_rag_chain)
):
    # 获取历史信息
    chat_history = memory.get_history(current_user.username)

    logger.info(f"User message: {request.message}")
    logger.info(f"Chat history: {chat_history}")

    # 调用链
    response = rag_chain.invoke(
        {
            "chat_history": chat_history,
            "input": request.message
        }
    )
    memory.add_message(
        current_user.username,
        HumanMessage(content=request.message)
    )

    memory.add_message(
        current_user.username,
        AIMessage(content=response["answer"])
    )
    references = []

    for doc in response["context"]:
        references.append(
            {
                "source": doc.metadata.get("source"),
                "content": doc.page_content
            }
        )

    return {
        "answer": response["answer"],
        "references": references
    }
