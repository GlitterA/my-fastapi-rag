from fastapi import APIRouter, Depends
from app.core.logger import logger
from app.schema.chat_schema import ChatBody
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import Runnable
from app.core.deps import get_rag_chain, get_chat_memory
from fastapi.responses import StreamingResponse
from app.rag.memory import ChatMemory

route = APIRouter()

@route.post("/test/chat")
async def chat_action(request: ChatBody,
                      rag_chain: Runnable = Depends(get_rag_chain),
                      memory: ChatMemory = Depends(get_chat_memory)):
    chat_history = memory.get_history(request.session_id)

    # 打印日志
    logger.info(f"User message: {request.message}")
    logger.info(f"Chat history: {chat_history}")

    # 流式输出调用链
    async def generate():
        full_response = ""

        async for chunk in rag_chain.astream(
                {
                    "chat_history": chat_history,
                    "input": request.message
                }
        ):
            full_response += chunk

            yield chunk

        # 更新历史
        memory.add_message(
            request.session_id,
            HumanMessage(content=request.message)

        )
        memory.add_message(
            request.session_id,
            AIMessage(content=full_response)
        )

    return StreamingResponse(
        generate(),
        media_type="text/plain"
    )
