import os
from typing import List, Dict, Any
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage

from app.services.document_processor import DocumentProcessor
from app.services.vector_store import VectorStoreService
from app.services.llm_service import LLMService

class ChatService:
    def __init__(self):
        self.doc_processor = DocumentProcessor()
        self.vector_store = VectorStoreService()
        self.llm_service = LLMService()
        self.llm = self.llm_service.get_llm()
        
        # RAG Prompt 模板
        self.prompt = ChatPromptTemplate.from_template("""
        Answer the following question based only on the provided context:

        <context>
        {context}
        </context>

        Question: {input}
        """)
        
        # 初始化 Chain (惰性加载，因为 retrieval 需要 vector store 有数据)
        self.qa_chain = None

    def process_and_index_files(self, file_paths: List[str]):
        """处理文件并建立索引"""
        all_docs = []
        for path in file_paths:
            print(f"Processing {path}...")
            docs = self.doc_processor.process_file(path)
            all_docs.extend(docs)
        
        if all_docs:
            print(f"Indexing {len(all_docs)} chunks...")
            self.vector_store.add_documents(all_docs)
            # 重置 chain 以使用新的检索器
            self._update_chain()
        
        return len(all_docs)

    def _update_chain(self):
        """更新 RAG Chain"""
        retriever = self.vector_store.get_retriever(search_kwargs={"k": 5})
        document_chain = create_stuff_documents_chain(self.llm, self.prompt)
        self.qa_chain = create_retrieval_chain(retriever, document_chain)

    def chat(self, question: str, chat_history: List[Dict] = None) -> Dict[str, Any]:
        """进行对话"""
        if not self.qa_chain:
            self._update_chain()
            
        # 简单的历史记录处理 (当前版本主要依赖 vector search，暂未将 history 传入 prompt 进行多轮意图理解)
        # 完整版应该使用 create_history_aware_retriever
        
        response = self.qa_chain.invoke({"input": question})
        
        return {
            "answer": response["answer"],
            "source_documents": response["context"]
        }

    def clear_knowledge_base(self):
        """清空知识库"""
        self.vector_store.clear()
        self.qa_chain = None

