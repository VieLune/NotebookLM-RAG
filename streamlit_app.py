import os
import shutil
import streamlit as st
from app.core.config import settings
from app.services.chat_service import ChatService

# 页面配置
st.set_page_config(page_title="GeminiDocAgent", layout="wide")

# 初始化 ChatService (单例模式)
@st.cache_resource
def get_chat_service():
    return ChatService()

chat_service = get_chat_service()

# 侧边栏：配置与文件上传
with st.sidebar:
    st.title("📚 文档管理")
    
    # API Key 检查
    if not settings.GEMINI_API_KEY:
        st.error("未检测到 GEMINI_API_KEY。请在 .env 文件中配置。")
        st.stop()

    uploaded_files = st.file_uploader(
        "上传文档 (PDF, TXT, DOCX, MD)", 
        type=['pdf', 'txt', 'docx', 'md', 'html'],
        accept_multiple_files=True
    )
    
    if st.button("处理并建立索引"):
        if not uploaded_files:
            st.warning("请先上传文件")
        else:
            with st.status("正在处理文档...", expanded=True) as status:
                # 1. 保存上传的文件到临时目录
                temp_dir = settings.UPLOAD_DIR
                saved_paths = []
                
                st.write("保存文件中...")
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    saved_paths.append(file_path)
                
                # 2. 调用服务处理
                st.write("解析与向量化...")
                try:
                    num_chunks = chat_service.process_and_index_files(saved_paths)
                    status.update(label="处理完成!", state="complete", expanded=False)
                    st.success(f"成功处理 {len(saved_paths)} 个文件，生成 {num_chunks} 个索引块。")
                except Exception as e:
                    st.error(f"处理失败: {str(e)}")
    
    if st.button("清空知识库"):
        chat_service.clear_knowledge_base()
        st.success("知识库已清空")

# 主界面：聊天
st.title("GeminiDocAgent 🤖")
st.caption("基于 Google Gemini Pro 的智能文档问答助手")

# 初始化聊天历史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示聊天历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 处理用户输入
if prompt := st.chat_input("关于文档有什么问题？"):
    # 1. 显示用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. 生成回答
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("思考中...")
        
        try:
            response = chat_service.chat(prompt)
            answer = response["answer"]
            sources = response["source_documents"]
            
            # 构建显示内容
            full_response = answer + "\n\n---\n**参考来源:**\n"
            seen_sources = set()
            for doc in sources:
                source_name = os.path.basename(doc.metadata.get("source", "Unknown"))
                page = doc.metadata.get("page", "N/A")
                if source_name not in seen_sources:
                    full_response += f"- `{source_name}` (Page {page})\n"
                    seen_sources.add(source_name)
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            error_msg = f"发生错误: {str(e)}"
            message_placeholder.error(error_msg)
