"""
SmartRAG 前端 — 对话 & 知识库 & 用户认证
使用方式: streamlit run frontend/app.py
"""
import streamlit as st
from api import RAGClient
import chat_ui
import knowledge_ui

# ═══════════════════════════════════════════════════════
# 页面配置（必须是第一个 Streamlit 命令）
# ═══════════════════════════════════════════════════════
st.set_page_config(
    page_title="SmartRAG",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════
# 全局 CSS
# ═══════════════════════════════════════════════════════
st.markdown(
    """
<style>
    /* 隐藏默认页脚和菜单 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* 登录页居中卡片 */
    .auth-container {
        max-width: 420px;
        margin: 8vh auto 0 auto;
        padding: 2rem;
        border-radius: 12px;
        background: #f8fafc;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }

    /* 聊天消息圆角微调 */
    .stChatMessage {
        border-radius: 12px !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ═══════════════════════════════════════════════════════
# 初始化
# ═══════════════════════════════════════════════════════
import os
API_URL = os.getenv("RAG_API_URL", "http://localhost:8000")
api = RAGClient(API_URL)

for key, default in {
    "token": None,
    "username": None,
    "authenticated": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ═══════════════════════════════════════════════════════
# 认证页
# ═══════════════════════════════════════════════════════
def render_auth():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            "<h1 style='text-align:center;margin-top:2rem;'>🤖 SmartRAG</h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='text-align:center;color:#888;'>智能知识检索问答系统</p>",
            unsafe_allow_html=True,
        )

    tab1, tab2 = st.tabs(["🔑 登录", "📝 注册"])

    with tab1:
        with st.form("login_form"):
            login_user = st.text_input("用户名", key="login_user")
            login_pass = st.text_input("密码", type="password", key="login_pass")
            submitted = st.form_submit_button("登录", use_container_width=True)
            if submitted:
                if not login_user or not login_pass:
                    st.error("请填写用户名和密码")
                else:
                    try:
                        data = api.login(login_user, login_pass)
                        st.session_state.token = data["access_token"]
                        st.session_state.username = login_user
                        st.session_state.authenticated = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"登录失败：{e}")

    with tab2:
        with st.form("register_form"):
            reg_user = st.text_input("用户名", key="reg_user")
            reg_pass = st.text_input("密码", type="password", key="reg_pass")
            reg_confirm = st.text_input("确认密码", type="password", key="reg_confirm")
            submitted = st.form_submit_button("注册", use_container_width=True)
            if submitted:
                if not reg_user or not reg_pass:
                    st.error("请填写用户名和密码")
                elif reg_pass != reg_confirm:
                    st.error("两次密码不一致")
                else:
                    try:
                        api.register(reg_user, reg_pass)
                        st.success("注册成功！请切换到登录页")
                        st.info("登录后即可使用")
                    except Exception as e:
                        st.error(f"注册失败：{e}")


# ═══════════════════════════════════════════════════════
# 主应用
# ═══════════════════════════════════════════════════════
def render_main():
    with st.sidebar:
        st.title("🤖 SmartRAG")

        # 用户信息
        st.caption(f"👤 {st.session_state.username}")

        # 后端状态
        try:
            api.list_documents(st.session_state.token)
            st.caption("🟢 后端连接正常")
        except Exception:
            st.caption("🔴 后端未连接")

        st.divider()

        # 导航
        page = st.radio(
            "导航",
            ["💬 对话", "📚 知识库"],
            label_visibility="collapsed",
        )

        st.divider()

        # 后端地址
        st.caption(f"API: {API_URL}")

        # 退出
        if st.button("🚪 退出登录", use_container_width=True):
            st.session_state.token = None
            st.session_state.username = None
            st.session_state.authenticated = False
            st.session_state.pop("messages", None)
            st.rerun()

    # 页面路由
    if page == "💬 对话":
        chat_ui.render(api)
    else:
        knowledge_ui.render(api)


# ═══════════════════════════════════════════════════════
# 入口
# ═══════════════════════════════════════════════════════
if not st.session_state.authenticated:
    render_auth()
else:
    render_main()
