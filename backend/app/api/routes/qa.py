import os.path
from typing import Any
import yaml
from fastapi import APIRouter
from app.core.logger import logger
from app.core.settings import settings
from app.schema.chat_schema import ChatBody
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI

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

model = ChatOpenAI(
    model=chat_config["LLM_MODEL"],
    api_key=settings.DASHSCOPE_API_KEY,
    base_url=settings.DASHSCOPE_BASE_URL
)

def get_context_retriever_chain(vector_store):
    """
    获得具有历史感知能力的检索链条
    """
    # 打印日志
    logger.info("创建上下文检索链")
    # 指定语言模型
    # model = ChatTongyi(
    #     model="qwen3.7-flash-2026-07-15",
    #     dashscope_api_key=settings.DASHSCOPE_API_KEY
    # )
    # 指定检索器

    # 指定prompt

    # 构造链


@route.post("/test/chat")
async def chat_action(request: ChatBody):
    response = model.invoke(
        request.message
    )
    return {
        "answer": response.content
    }
