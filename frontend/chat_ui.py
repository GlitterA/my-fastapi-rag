"""
会话页 — 流式对话 + 会话历史 + 来源引用
使用 st.fragment + st.bottom 隔离聊天区域
"""

import streamlit as st


def render(api):
    st.title("💬 会话")

    # 初始化消息历史
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 聊天核心
    _chat_fragment(api)

    # ── 侧边栏操作 ───────────────────────────────────
    with st.sidebar:
        st.divider()

        if st.button("🗑️ 清空对话记录", use_container_width=True):
            st.session_state.messages = []
            st.rerun()


@st.fragment
def _chat_fragment(api):
    """聊天核心：历史 + 输入 + 流式回答"""

    # ── 渲染已有消息 ─────────────────────────────────
    for msg in st.session_state.messages:

        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            if msg.get("sources"):
                _show_sources(msg["sources"])

    # ── 底部输入框 ───────────────────────────────────
    #
    # st.chat_input 放在 fragment 里会变成 inline 输入框，
    # 所以使用 st.bottom 将它固定到页面底部。
    #
    with st.bottom:
        prompt = st.chat_input(
            "请输入你的问题，系统将基于知识库进行回答",
            key="chat_input",
        )

    # ── 用户发送消息 ─────────────────────────────────
    if prompt:

        # 立即显示用户消息
        with st.chat_message("user"):
            st.markdown(prompt)

        # 保存用户消息
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
        })

        # ── AI 流式回答 ──────────────────────────────
        with st.chat_message("assistant"):

            placeholder = st.empty()
            full_response = ""
            sources = []

            try:
                for event in api.chat_stream(
                    prompt,
                    st.session_state.token,
                ):
                    event_type = event.get("type")

                    # AI token
                    if event_type == "token":
                        content = event.get("data", "")
                        full_response += content

                        placeholder.markdown(
                            full_response + "▌"
                        )

                    # 来源
                    elif event_type == "sources":
                        sources = event.get("data", [])

                    # 后端错误
                    elif event_type == "error":
                        placeholder.error(
                            event.get("data", "未知错误")
                        )
                        full_response = ""
                        break

            except Exception as e:
                placeholder.error(f"请求失败：{e}")
                full_response = ""

            # ── 流式完成 ──────────────────────────────
            if full_response:

                # 去掉光标
                placeholder.markdown(full_response)

                # 保存 AI 消息
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response,
                    "sources": sources,
                })

                # 显示来源
                if sources:
                    _show_sources(sources)


def _show_sources(sources: list[dict]):
    """显示参考来源面板"""

    with st.expander(
        f"📖 参考来源（{len(sources)} 条）"
    ):
        for i, src in enumerate(sources, 1):

            source_name = src.get(
                "source",
                f"文档 #{i}",
            )

            st.caption(
                f"**{i}. {source_name}**"
            )

            content = src.get("content", "")

            st.text(content[:300])

            if len(content) > 300:
                st.caption("*... 内容已截断*")

            if i < len(sources):
                st.divider()