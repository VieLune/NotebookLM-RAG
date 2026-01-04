import os
from typing import List
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
    UnstructuredMarkdownLoader,
    BSHTMLLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from app.core.config import settings

class DocumentProcessor:
    def __init__(self):
        self.supported_extensions = {
            ".pdf": PyPDFLoader,
            ".txt": TextLoader,
            ".docx": Docx2txtLoader,
            ".md": UnstructuredMarkdownLoader,
            ".html": BSHTMLLoader
        }
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""]
        )

    def load_document(self, file_path: str) -> List[Document]:
        """加载单个文档"""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext not in self.supported_extensions:
            raise ValueError(f"Unsupported file format: {file_ext}")
            
        loader_cls = self.supported_extensions[file_ext]
        
        # 针对不同 loader 的特殊处理
        if file_ext == ".txt":
            loader = loader_cls(file_path, encoding="utf-8")
        else:
            loader = loader_cls(file_path)
            
        return loader.load()

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """将文档分割为 chunk"""
        return self.text_splitter.split_documents(documents)

    def process_file(self, file_path: str) -> List[Document]:
        """加载并分割文件的快捷方法"""
        docs = self.load_document(file_path)
        return self.split_documents(docs)

