from pathlib import Path
import os

os.chdir(Path(__file__).resolve().parent.parent)
from app.core.db import get_session
from app.rag.ingest import ingest_file
from app.crud.file_crud import get_file_by_filename, save_file
from app.rag.vectorstore import init_vector_store

BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = BASE_DIR / "data" / "knowledge"

UPLOADER = "system"


def main():
    print("=" * 60)
    print("初始化知识库")
    print("=" * 60)

    print(f"\n知识库目录：{KNOWLEDGE_DIR}")

    files = list(KNOWLEDGE_DIR.glob("*"))

    if not files:
        print("没有找到文件")
        return

    print(f"\n发现 {len(files)} 个文件：")

    for file_path in files:
        print(f"  - {file_path.name}")

    # 获取向量库（ingest_file 内部按 chunk_id 判重，重复执行安全）
    vector_store = init_vector_store()

    # 获取数据库 session
    session = next(get_session())

    try:
        for file_path in files:

            if not file_path.is_file():
                continue

            filename = file_path.name

            print("\n" + "-" * 60)
            print(f"正在处理：{filename}")

            # 写 File 表
            existing = get_file_by_filename(
                filename=filename,
                uploader_name=UPLOADER,
                session=session
            )

            if existing:
                print(f"[跳过数据库] 已存在：{filename}")
            else:
                save_file(
                    filename=filename,
                    uploader_name=UPLOADER,
                    session=session
                )
                print(f"[数据库] 已登记：{filename}")

            # 写向量库
            ingest_file(
                file_path=file_path,
                vector_store=vector_store,
                uploader=UPLOADER,
                filename=filename
            )

            print(f"[向量库] 已完成：{filename}")

    finally:
        session.close()

    print("\n" + "=" * 60)
    print("知识库初始化完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
