from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pathlib import Path
from app.config.config_loader import load_yaml_configs

CONFIG_DIR = Path(__file__).parent

class ChatConfig(BaseModel):
    llm_model: str = "qwen3.7-plus"
    max_history: int = 10
    save_dir: Path = Path("data/chat_history")


class SplitterConfig(BaseModel):
    chunk_size: int = 500
    chunk_overlap: int = 50


class Config(BaseModel):
    chat: ChatConfig
    splitter: SplitterConfig


configs = Config(**load_yaml_configs(CONFIG_DIR))