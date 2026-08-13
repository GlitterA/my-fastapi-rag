"""
SmartRAG API 客户端
封装所有后端接口调用，统一处理鉴权和异常
"""
import json
import httpx
from typing import Generator


class RAGClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")

    # ── 认证 ────────────────────────────────────────────

    def register(self, username: str, password: str) -> dict:
        resp = httpx.post(
            f"{self.base_url}/create",
            json={"username": username, "password": password},
            timeout=10,
        )
        self._raise_for_status(resp)
        return resp.json()

    def login(self, username: str, password: str) -> dict:
        """返回 {'access_token': str, 'token_type': str}"""
        resp = httpx.post(
            f"{self.base_url}/login/access-token",
            data={"username": username, "password": password},
            timeout=10,
        )
        self._raise_for_status(resp)
        return resp.json()

    # ── 问答 ────────────────────────────────────────────

    def chat(self, message: str, token: str) -> dict:
        """非流式问答"""
        resp = httpx.post(
            f"{self.base_url}/qa/chat",
            json={"message": message},
            headers=self._auth(token),
            timeout=60,
        )
        self._raise_for_status(resp)
        return resp.json()

    def chat_stream(self, message: str, token: str) -> Generator[dict, None, None]:
        """流式问答，逐行返回 NDJSON 事件
        事件类型: {'type': 'token', 'data': '...'}
                  {'type': 'sources', 'data': [...]}
                  {'type': 'error', 'data': '...'}
        """
        with httpx.stream(
            "POST",
            f"{self.base_url}/qa/stream_chat",
            json={"message": message},
            headers=self._auth(token),
            timeout=None,
        ) as resp:
            self._raise_for_status(resp)
            for line in resp.iter_lines():
                if line:
                    yield json.loads(line)

    # ── 知识库 ──────────────────────────────────────────

    def upload_document(self, file_bytes: bytes, filename: str, token: str) -> dict:
        resp = httpx.post(
            f"{self.base_url}/documents/upload",
            files={"file": (filename, file_bytes, "application/octet-stream")},
            headers=self._auth(token),
            timeout=120,
        )
        self._raise_for_status(resp)
        return resp.json()

    def list_documents(self, token: str) -> list[dict]:
        resp = httpx.get(
            f"{self.base_url}/documents",
            headers=self._auth(token),
            timeout=10,
        )
        self._raise_for_status(resp)
        return resp.json()

    def delete_document(self, filename: str, token: str) -> dict:
        resp = httpx.delete(
            f"{self.base_url}/documents/{filename}",
            headers=self._auth(token),
            timeout=10,
        )
        self._raise_for_status(resp)
        return resp.json()

    # ── 工具 ────────────────────────────────────────────

    @staticmethod
    def _auth(token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}

    @staticmethod
    def _raise_for_status(resp: httpx.Response):
        if resp.is_error:
            detail = "未知错误"
            try:
                detail = resp.json().get("detail", detail)
            except Exception:
                detail = resp.text[:200]
            raise httpx.HTTPStatusError(
                f"{resp.status_code}: {detail}",
                request=resp.request,
                response=resp,
            )
