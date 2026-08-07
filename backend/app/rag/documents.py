# 负责加载不同格式文件转为Document对象

from langchain_core.documents import Document
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders.json_loader import JSONLoader
from langchain_community.document_loaders.text import TextLoader
from langchain_community.document_loaders.pdf import PyPDFLoader

from pathlib import Path

LOADER_MAP = {
    ".csv": lambda file: CSVLoader(
        file_path=file,
        encoding="utf-8"
    ),

    ".json": lambda file: JSONLoader(
        file_path=file,
        jq_schema="."
    ),

    ".txt": lambda file: TextLoader(
        file_path=file,
        encoding="utf-8"
    ),

    ".pdf": lambda file: PyPDFLoader(
        file_path=file,
        mode="page"
    )
}


def load_files(directory: Path) -> list[Document]:
    """
    加载 directory 下的所有文档
    """
    documents = []

    for file in Path(directory).iterdir():

        suffix = file.suffix.lower()

        if suffix not in LOADER_MAP:
            raise ValueError(
                f"不支持的文件格式: {suffix}"
            )

        loader = LOADER_MAP[suffix](file)

        documents.extend(
            loader.load()
        )

    return documents

def load_file(
        file_path: Path
) -> list[Document]:
    suffix = file_path.suffix.lower()

    if suffix not in LOADER_MAP:
        raise ValueError(
            f"不支持的文件格式：{suffix}"
        )

    loader = LOADER_MAP[suffix](file_path)

    return loader.load()



