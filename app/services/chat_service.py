import os
from typing import List, Dict, Any
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

from app.core.config import settings
from app.services.document_processor import DocumentProcessor
from app.services.vector_store import VectorStoreService
from app.services.llm_service import LLMService

class ChatService:
    def __init__(self):
        self.doc_processor = DocumentProcessor()
        self.vector_store = VectorStoreService()
        self.llm_service = LLMService()
        self.llm = self.llm_service.get_llm()
        
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
        """更新 RAG Chain，增加历史记录感知能力"""
        retriever = self.vector_store.get_retriever(search_kwargs={"k": settings.SEARCH_TOP_K})
        
        # 1. 历史感知检索器 (History Aware Retriever)
        # 负责将"整合了历史上下文的问题"重写为"独立问题"
        contextualize_q_system_prompt = (
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, "
            "just reformulate it if needed and otherwise return it as is."
        )
        
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        
        history_aware_retriever = create_history_aware_retriever(
            self.llm, retriever, contextualize_q_prompt
        )
        
        # 2. 问答链 (QA Chain)
        # 负责根据检索到的文档回答问题
        qa_system_prompt = """Answer the following question based only on the provided context.
        If you cannot answer the question based on the context, please politely say so.
        
        <context>
        {context}
        </context>"""
        
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", qa_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        
        document_chain = create_stuff_documents_chain(self.llm, qa_prompt)
        
        # 3. 最终的 RAG 链
        self.qa_chain = create_retrieval_chain(history_aware_retriever, document_chain)

    def chat(self, question: str, chat_history: List[Dict] = None) -> Dict[str, Any]:
        """进行对话"""
        if not self.qa_chain:
            self._update_chain()
            
        # 处理历史记录格式
        langchain_history = []
        if chat_history:
            for msg in chat_history:
                if msg["role"] == "user":
                    langchain_history.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    langchain_history.append(AIMessage(content=msg["content"]))
        
        response = self.qa_chain.invoke({
            "input": question,
            "chat_history": langchain_history
        })
        
        return {
            "answer": response["answer"],
            "source_documents": response["context"]
        }

    def chat_stream(self, question: str, chat_history: List[Dict] = None):
        """流式对话"""
        if not self.qa_chain:
            self._update_chain()
            
        # 处理历史记录格式
        langchain_history = []
        if chat_history:
            for msg in chat_history:
                if msg["role"] == "user":
                    langchain_history.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    langchain_history.append(AIMessage(content=msg["content"]))
        
        chain_input = {
            "input": question,
            "chat_history": langchain_history
        }
        
        for chunk in self.qa_chain.stream(chain_input):
            if "answer" in chunk:
                yield {"type": "answer", "content": chunk["answer"]}
            if "context" in chunk:
                yield {"type": "source", "content": chunk["context"]}

    def clear_knowledge_base(self):
        """清空知识库"""
        self.vector_store.clear()
        self.qa_chain = None
