# 负责提供不同种类的切分器

import os
from typing import Any
import yaml
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 设置配置文件路径
config_path = os.path.join(os.path.dirname(__file__), "..", "config/splitter.yaml")

# 读取配置文件
with open(config_path, "r", encoding="utf-8") as config_file:
    config: dict[str, Any] = yaml.safe_load(config_file)
splitter_config = config.get("SPLITTER_CONFIG", {})

recursive_character_text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=splitter_config["CHUNK_SIZE"],
    chunk_overlap=splitter_config["CHUNK_OVERLAP"],
    separators=["\n\n", "\n", "。", "!", "?", ".", "!", "？", " ", "", ],
    length_function=len
)

def get_text_splitter():
    return recursive_character_text_splitter
