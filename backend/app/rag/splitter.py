# 负责提供不同种类的切分器

from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import config

recursive_character_text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=config.splitter.chunk_size,
    chunk_overlap=config.splitter.chunk_overlap,
    separators=["\n\n", "\n", "。", "!", "?", ".", "!", "？", " ", "", ],
    length_function=len
)

def get_text_splitter():
    return recursive_character_text_splitter
