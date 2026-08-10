# 进行RAG的记忆管理
import os
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from pathlib import Path
import json
from loguru import logger
from app.config import configs

class ChatMemory:

    def __init__(self):
        """
        cache = {
            "user_a":[
                HumanMessage(...),
                AIMessage(...)
            ],
            "user_b":[
                HumanMessage(...),
                AIMessage(...)
            ]
        }
        """
        # 最大历史对话条目数
        self.max_history_len = configs.chat.max_history
        # 本地存储路径
        self.save_dir = Path(configs.chat.save_dir)
        self.save_dir.mkdir(
            parents=True,
            exist_ok=True
        )
        # 对话缓存
        self.cache: dict[str, list[BaseMessage]] = {}

    def _get_file(
            self,
            session_id: str
    ) -> Path:
        """
        获取当前session_id用户的历史jsonl文件的Path对象
        """
        return Path(os.path.join(self.save_dir, f"{session_id}.jsonl"))

    def load_from_file(
            self,
            session_id: str
    ) -> list[BaseMessage]:
        file = self._get_file(session_id)
        if not file.exists():
            return []

        with open(file, "r", encoding="utf-8") as f:
            messages = []
            for line in f:
                item = json.loads(line)
                if item["type"] == "human":
                    messages.append(HumanMessage(content=item["content"]))
                elif item["type"] == "ai":
                    messages.append(AIMessage(content=item["content"]))

        return messages[-self.max_history_len:]

    def append_to_file(
            self,
            session_id: str,
            message: BaseMessage
    ):

        file = self._get_file(session_id)
        logger.info(f"存储路径：{file}")

        if isinstance(message, HumanMessage):
            data = {
                "type": "human",
                "content": message.content
            }

        elif isinstance(message, AIMessage):
            data = {
                "type": "ai",
                "content": message.content
            }

        else:
            raise ValueError(
                "不支持的消息类型"
            )

        with open(file, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

    def get_history(
            self,
            session_id: str
    ) -> list[BaseMessage]:
        """
        获得session_id用户的历史信息
        """

        # 查内存
        if session_id in self.cache:
            return self.cache[session_id]

        # 从文件恢复
        history = self.load_from_file(session_id)

        # 放入内存
        self.cache[session_id] = history

        return history

    def add_message(
            self,
            session_id: str,
            message: BaseMessage,
    ):

        # 更新内存
        history = self.get_history(session_id)
        history.append(message)
        if len(history) > self.max_history_len:
            history[:] = history[-self.max_history_len:]


        # 持久化
        self.append_to_file(session_id, message)

    def clear_cache(self, session_id: str):
        if session_id in self.cache:
            del self.cache[session_id]
