"""
MiniNotebookLM - Streamlit 应用入口
基于 LangChain 和 Gemini API 的 RAG 应用
"""
import streamlit as st
import tempfile
import os
from rag_engine import NotebookLMEngine

# 页面配置
st.set_page_config(
    page_title="Mini NotebookLM",
    page_icon="📚",
    layout="wide"
)

# 初始化 session_state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = None

if "api_key_set" not in st.session_state:
    st.session_state.api_key_set = False

if "documents_processed" not in st.session_state:
    st.session_state.documents_processed = False

# 侧边栏
with st.sidebar:
    st.header("⚙️ 配置")
    
    # API Key 输入
    api_key = st.text_input(
        "Google API Key",
        type="password",
        help="请输入您的 Google Gemini API Key",
        value=st.session_state.get("api_key", "")
    )
    
    # 保存 API Key 到 session_state
    if api_key and api_key != st.session_state.get("api_key", ""):
        st.session_state.api_key = api_key
        # 如果 API Key 改变，重置引擎
        if st.session_state.rag_engine is not None:
            st.session_state.rag_engine = None
            st.session_state.documents_processed = False
            st.rerun()
    
    st.divider()
    
    # 文件上传
    st.subheader("📄 文档上传")
    uploaded_file = st.file_uploader(
        "上传 PDF 文档",
        type=["pdf"],
        help="支持上传 PDF 格式的文档"
    )
    
    # 处理文档按钮
    process_button = st.button(
        "🔄 处理文档",
        type="primary",
        disabled=not (api_key and uploaded_file),
        use_container_width=True
    )
    
    # 显示状态信息
    st.divider()
    st.subheader("📊 状态")
    
    if api_key:
        st.success("✅ API Key 已设置")
    else:
        st.warning("⚠️ 请先输入 API Key")
    
    if st.session_state.documents_processed:
        st.success("✅ 文档已处理")
    else:
        st.info("ℹ️ 等待处理文档")
    
    # 清空聊天记录按钮
    if st.session_state.messages:
        st.divider()
        if st.button("🗑️ 清空聊天记录", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

# 处理文档
if process_button and api_key and uploaded_file:
    try:
        # 初始化或获取 RAG 引擎
        if st.session_state.rag_engine is None:
            with st.spinner("正在初始化 RAG 引擎..."):
                st.session_state.rag_engine = NotebookLMEngine(api_key)
        
        # 保存上传的文件到临时目录
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name
        
        # 处理文档
        with st.spinner("正在处理文档，请稍候..."):
            success = st.session_state.rag_engine.ingest_file(tmp_path)
            
            if success:
                st.session_state.documents_processed = True
                st.success("✅ 文档处理成功！现在可以开始提问了。")
                # 清理临时文件
                os.unlink(tmp_path)
            else:
                st.error("❌ 文档处理失败")
                os.unlink(tmp_path)
                
    except Exception as e:
        st.error(f"❌ 处理文档时出错: {str(e)}")
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)

# 主聊天区
st.title("📚 Mini NotebookLM")
st.caption("基于文档的智能问答系统")

# 显示聊天历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 聊天输入框
if prompt := st.chat_input("请输入您的问题..."):
    # 检查前置条件
    if not api_key:
        st.warning("⚠️ 请先在侧边栏输入 API Key")
    elif not st.session_state.documents_processed:
        st.warning("⚠️ 请先上传并处理文档")
    else:
        # 添加用户消息到聊天历史
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 显示用户消息
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 生成 AI 回答
        with st.chat_message("assistant"):
            with st.spinner("正在思考..."):
                try:
                    # 确保 RAG 引擎已初始化
                    if st.session_state.rag_engine is None:
                        st.session_state.rag_engine = NotebookLMEngine(api_key)
                        # 尝试加载已有数据库
                        st.session_state.rag_engine.load_existing_db()
                    
                    # 获取回答
                    answer = st.session_state.rag_engine.get_answer(prompt)
                    
                    # 显示回答
                    st.markdown(answer)
                    
                    # 添加 AI 回答到聊天历史
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                except Exception as e:
                    error_msg = f"❌ 生成回答时出错: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

