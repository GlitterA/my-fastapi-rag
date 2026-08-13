from pathlib import Path
import shutil
import sqlite3


# 项目目录
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

DB_PATH = DATA_DIR / "SQLite" / "app.db"


# 需要清理的 RAG 数据
TARGETS = [
    DATA_DIR / "chroma",
    DATA_DIR / "test_chroma",
    DATA_DIR / "uploads",
    DATA_DIR / "chat_history",
    DATA_DIR / "test_chat_history",
]


def remove_path(path: Path):
    """删除文件或目录"""

    if not path.exists():
        print(f"[跳过] 不存在: {path}")
        return

    if path.is_dir():
        shutil.rmtree(path)
        print(f"[删除目录] {path}")
    else:
        path.unlink()
        print(f"[删除文件] {path}")


def clear_file_records():
    """清空 File 表"""

    print("\n[数据库] 清空 File 表...")

    if not DB_PATH.exists():
        print(f"[跳过] 数据库不存在: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)

    try:
        cursor = conn.cursor()

        cursor.execute("DELETE FROM file")

        conn.commit()

        print(f"[数据库] File 表已清空，共删除 {cursor.rowcount} 条记录")

    finally:
        conn.close()


def main():

    print("=" * 60)
    print("Reset RAG Data")
    print("=" * 60)

    print(f"\n项目目录:")
    print(f"  {BASE_DIR}")

    print(f"\n数据库:")
    print(f"  {DB_PATH}")

    print(f"\n以下 RAG 数据将被删除:")

    for path in TARGETS:
        print(f"  - {path}")

    print("\n数据库中的以下数据将被清空:")
    print(f"  - File 表")

    print("\n以下数据会被保留:")
    print(f"  - {DATA_DIR / 'knowledge'}")
    print("    ↑ 原始知识库文件")
    print(f"  - User 表")
    print("    ↑ 用户数据")

    confirm = input("\n确认删除？输入 y/Y 继续：")

    if confirm.lower() != "y":
        print("已取消。")
        return

    # --------------------------------------------------------
    # 删除 RAG 文件 / 向量数据
    # --------------------------------------------------------

    for path in TARGETS:
        remove_path(path)

    # --------------------------------------------------------
    # 清空 File 表
    # --------------------------------------------------------

    clear_file_records()

    print("\n" + "=" * 60)
    print("RAG 数据清理完成")
    print("=" * 60)


if __name__ == "__main__":
    main()