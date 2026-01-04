"""
RAG Engine - 检索增强生成引擎
基于 LangChain 和 Gemini API 实现
类似 NotebookLM 的文档问答系统
"""
import os
from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate


class NotebookLMEngine:
    """
    NotebookLM 风格的 RAG 引擎类
    负责文档加载、向量化、检索和生成
    """
    
    def __init__(self, api_key: str):
        """
        初始化 NotebookLM 引擎
        
        Args:
            api_key: Google Gemini API Key
        """
        if not api_key:
            raise ValueError("API Key 不能为空")
        
        self.api_key = api_key
        self.model_name = "gemini-1.5-flash"
        self.embedding_model = "models/embedding-001"
        self.db_path = "./db"
        
        # 初始化 LLM
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=self.api_key,
                temperature=0.7,
                convert_system_message_to_human=True
            )
        except Exception as e:
            raise RuntimeError(f"初始化 LLM 失败: {str(e)}")
        
        # 初始化 Embeddings
        try:
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=self.embedding_model,
                google_api_key=self.api_key
            )
        except Exception as e:
            raise RuntimeError(f"初始化 Embeddings 失败: {str(e)}")
        
        # 初始化文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # 向量存储（延迟初始化）
        self.vectorstore: Optional[Chroma] = None
        self.retriever = None
        
        # 检索链（延迟初始化）
        self.qa_chain = None
    
    def ingest_file(self, file_path: str) -> bool:
        """
        处理并导入 PDF 文件到向量数据库
        
        Args:
            file_path: PDF 文件路径
            
        Returns:
            bool: 是否成功导入
            
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 文件格式不支持
            RuntimeError: 处理过程中的其他错误
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        if not file_path.lower().endswith('.pdf'):
            raise ValueError(f"不支持的文件格式，仅支持 PDF: {file_path}")
        
        try:
            # 加载 PDF 文档
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            if not documents:
                raise ValueError(f"PDF 文件为空或无法读取: {file_path}")
            
            # 切分文档
            splits = self.text_splitter.split_documents(documents)
            
            if not splits:
                raise ValueError(f"文档切分后为空: {file_path}")
            
            # 创建或更新向量存储
            if self.vectorstore is None:
                # 创建新的向量存储
                self.vectorstore = Chroma.from_documents(
                    documents=splits,
                    embedding=self.embeddings,
                    persist_directory=self.db_path
                )
            else:
                # 添加到现有向量存储
                self.vectorstore.add_documents(splits)
                self.vectorstore.persist()
            
            # 创建检索器
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 4}  # 检索前 4 个最相关的文档块
            )
            
            # 构建检索链
            self._build_qa_chain()
            
            return True
            
        except Exception as e:
            raise RuntimeError(f"处理文件失败: {str(e)}")
    
    def _build_qa_chain(self):
        """构建问答检索链"""
        if self.retriever is None:
            raise RuntimeError("检索器未初始化，请先导入文档")
        
        # NotebookLM 风格的专业 Prompt
        prompt_template = """你是一位专业、富有洞察力的领域专家助手，类似于 NotebookLM。你的核心职责是基于提供的文档上下文，为用户提供准确、深入的分析和回答。

## 核心原则

**严格基于上下文（Strict Grounding）：**
- **只能**使用提供的文档上下文中的信息来回答问题
- **严禁**编造、推测或使用上下文之外的知识
- 如果上下文中没有相关信息，必须明确说明"根据提供的文档，我无法找到相关信息"或"文档中未提及此内容"
- 不要基于常识或外部知识进行补充，即使你认为这些信息是正确的

**回答风格：**
- 语气专业、富有洞察力，像一位在该领域的资深专家
- 使用清晰、有条理的结构化表达
- 适当使用 Markdown 格式（加粗、列表、标题等）提升可读性
- 在关键信息处引用原文，使用引号标注具体内容

**文档上下文：**
{context}

**用户问题：**
{input}

请基于上述文档上下文，以专业、结构化的方式回答用户的问题。如果上下文中没有相关信息，请明确说明。"""

        prompt = ChatPromptTemplate.from_template(prompt_template)
        
        # 创建文档链
        document_chain = create_stuff_documents_chain(
            llm=self.llm,
            prompt=prompt
        )
        
        # 创建检索链
        self.qa_chain = create_retrieval_chain(
            retriever=self.retriever,
            combine_docs_chain=document_chain
        )
    
    def get_answer(self, query: str) -> str:
        """
        基于已导入的文档回答用户问题
        
        Args:
            query: 用户问题
            
        Returns:
            str: 回答内容
            
        Raises:
            RuntimeError: 如果向量库未初始化或检索链未构建
            ValueError: 如果查询为空
        """
        if not query or not query.strip():
            raise ValueError("查询问题不能为空")
        
        if self.qa_chain is None:
            # 尝试从现有数据库加载
            if os.path.exists(self.db_path) and os.listdir(self.db_path):
                try:
                    self.vectorstore = Chroma(
                        persist_directory=self.db_path,
                        embedding_function=self.embeddings
                    )
                    self.retriever = self.vectorstore.as_retriever(
                        search_type="similarity",
                        search_kwargs={"k": 4}
                    )
                    self._build_qa_chain()
                except Exception as e:
                    raise RuntimeError(
                        f"无法加载向量数据库，请先导入文档。错误: {str(e)}"
                    )
            else:
                raise RuntimeError(
                    "向量数据库未初始化，请先使用 ingest_file() 导入文档"
                )
        
        try:
            # 执行检索和生成
            result = self.qa_chain.invoke({"input": query})
            
            # 提取回答内容
            answer = result.get("answer", "抱歉，无法生成回答。")
            
            # 提取并格式化 Source Attribution
            context_docs = result.get("context", [])
            source_attribution = self._format_source_attribution(context_docs)
            
            # 将 Source Attribution 附加到回答末尾
            if source_attribution:
                answer = f"{answer}\n\n---\n\n**参考来源：**\n{source_attribution}"
            
            return answer
            
        except Exception as e:
            raise RuntimeError(f"生成回答时出错: {str(e)}")
    
    def _format_source_attribution(self, context_docs) -> str:
        """
        格式化 Source Attribution，展示参考的文档片段信息
        
        Args:
            context_docs: 检索到的文档列表
            
        Returns:
            str: 格式化后的来源信息
        """
        if not context_docs:
            return ""
        
        # 确保 context_docs 是列表
        if not isinstance(context_docs, list):
            return ""
        
        sources = []
        seen_sources = set()
        
        for i, doc in enumerate(context_docs, 1):
            # 提取文档元数据
            metadata = doc.metadata if hasattr(doc, 'metadata') else {}
            
            # 构建来源标识
            source_info = []
            
            # 文件名
            if 'source' in metadata:
                source_path = metadata['source']
                # 提取文件名（去除路径）
                filename = os.path.basename(source_path) if source_path else "未知文档"
                source_info.append(f"**文档：** {filename}")
            
            # 页码
            if 'page' in metadata:
                page_num = metadata['page']
                # 页码从0开始，显示时+1
                try:
                    page_display = int(page_num) + 1
                    source_info.append(f"**页码：** {page_display}")
                except (ValueError, TypeError):
                    source_info.append(f"**页码：** {page_num}")
            
            # 如果没有任何元数据，至少显示文档序号
            if not source_info:
                source_info.append(f"**文档片段 {i}**")
            
            # 创建唯一标识符（避免重复）
            source_key = f"{metadata.get('source', '')}_{metadata.get('page', '')}"
            if source_key not in seen_sources:
                seen_sources.add(source_key)
                sources.append("- " + " | ".join(source_info))
        
        return "\n".join(sources) if sources else ""
    
    def load_existing_db(self) -> bool:
        """
        加载已存在的向量数据库
        
        Returns:
            bool: 是否成功加载
        """
        if not os.path.exists(self.db_path) or not os.listdir(self.db_path):
            return False
        
        try:
            self.vectorstore = Chroma(
                persist_directory=self.db_path,
                embedding_function=self.embeddings
            )
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 4}
            )
            self._build_qa_chain()
            return True
        except Exception as e:
            raise RuntimeError(f"加载向量数据库失败: {str(e)}")
    
    def clear_db(self) -> bool:
        """
        清空向量数据库
        
        Returns:
            bool: 是否成功清空
        """
        try:
            if os.path.exists(self.db_path):
                import shutil
                shutil.rmtree(self.db_path)
            self.vectorstore = None
            self.retriever = None
            self.qa_chain = None
            return True
        except Exception as e:
            raise RuntimeError(f"清空数据库失败: {str(e)}")

