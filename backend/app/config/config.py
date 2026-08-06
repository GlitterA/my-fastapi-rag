from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pathlib import Path
import yaml

CONFIG_DIR = Path(__file__).parent


class ChatConfig(BaseModel):
    llm_model: str = "qwen3.7-plus"
    max_history: int = 10
    save_dir: Path = Path("data/chat_history")


class SplitterConfig(BaseModel):
    chunk_size: int = 500
    chunk_overlap: int = 50


class Config(BaseSettings):
    chat: ChatConfig
    splitter: SplitterConfig


def _load_config() -> Config:
    """加载多个 YAML 文件并合并"""
    merged: dict = {}
    for yaml_file in (CONFIG_DIR / "chat.yaml", CONFIG_DIR / "splitter.yaml"):
        with open(yaml_file, encoding="utf-8") as f:
            merged.update(yaml.safe_load(f))
    return Config(**merged)


config = _load_config()
