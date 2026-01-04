from typing import List, Optional
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from app.core.config import settings
import google.generativeai as genai

class VectorStoreService:
    def __init__(self):
        # 配置 Google API
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in environment variables")
            
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # 初始化 Embedding 模型
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=settings.GEMINI_API_KEY
        )
        
        # 初始化向量数据库路径
        self.persist_directory = settings.VECTOR_DB_DIR
        self.collection_name = settings.COLLECTION_NAME
        
        # 加载或创建向量存储
        self.vector_store = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name=self.collection_name
        )

    def add_documents(self, documents: List[Document]):
        """将文档向量化并存储"""
        if not documents:
            return
            
        # Chroma 自动处理分批和存储
        self.vector_store.add_documents(documents)
        self.vector_store.persist()
        
    def search(self, query: str, k: int = 4) -> List[Document]:
        """相似度搜索"""
        return self.vector_store.similarity_search(query, k=k)

    def get_retriever(self, search_kwargs: dict = None):
        """获取检索器对象，用于 Chain"""
        if search_kwargs is None:
            search_kwargs = {"k": 4}
        return self.vector_store.as_retriever(search_kwargs=search_kwargs)

    def clear(self):
        """清空向量库 (慎用)"""
        self.vector_store.delete_collection()
        self.vector_store = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name=self.collection_name
        )

