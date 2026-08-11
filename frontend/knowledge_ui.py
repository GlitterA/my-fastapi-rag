"""
知识库页 — 文档上传 / 列表 / 删除
"""
import streamlit as st


def render(api):
    st.title("📚 知识库管理")

    # ── 上传区域 ─────────────────────────────────────
    st.subheader("📤 上传文档")

    uploaded_file = st.file_uploader(
        "拖拽或点击上传，支持 TXT / PDF / CSV / JSON",
        type=["txt", "pdf", "csv", "json"],
        key="doc_uploader",
    )

    if uploaded_file:
        with st.spinner(f"正在处理 **{uploaded_file.name}** ..."):
            try:
                result = api.upload_document(
                    uploaded_file.read(),
                    uploaded_file.name,
                    st.session_state.token,
                )
                st.success(f"✅ {result.get('message', '上传成功')}")
                st.rerun()
            except Exception as e:
                st.error(f"上传失败：{e}")

    st.divider()

    # ── 文档列表 ─────────────────────────────────────
    st.subheader("📋 已上传文档")

    try:
        docs = api.list_documents(st.session_state.token)
    except Exception as e:
        st.error(f"获取文档列表失败：{e}")
        docs = []

    if not docs:
        st.info("📭 暂无文档，请上传知识文件以开始使用")
        return

    # 表格展示 + 操作
    for doc in docs:
        with st.container():
            c1, c2 = st.columns([6, 1])
            with c1:
                st.write(f"📄 {doc['filename']}")
            with c2:
                if st.button("🗑 删除", key=f"del_{doc['filename']}", use_container_width=True):
                    try:
                        api.delete_document(doc["filename"], st.session_state.token)
                        st.success("已删除")
                        st.rerun()
                    except Exception as e:
                        st.error(f"删除失败：{e}")
