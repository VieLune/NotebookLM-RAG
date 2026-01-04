import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class Config:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        
        # Gemini 配置
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.GEMINI_MODEL = self.config.get("gemini", {}).get("model", "gemini-2.5-flash")
        self.GEMINI_TEMPERATURE = self.config.get("gemini", {}).get("temperature", 0.3)
        self.GEMINI_MAX_TOKENS = self.config.get("gemini", {}).get("max_tokens", 2000)
        
        # 向量存储配置
        self.VECTOR_STORE_TYPE = self.config.get("vector_store", {}).get("type", "chroma")
        self.VECTOR_DB_DIR = self.config.get("vector_store", {}).get("persist_directory", "./data/vector_db")
        self.COLLECTION_NAME = self.config.get("vector_store", {}).get("collection_name", "gemini_doc_agent")
        self.SEARCH_TOP_K = self.config.get("vector_store", {}).get("search_top_k", 10)
        
        # 文档处理配置
        self.CHUNK_SIZE = self.config.get("document", {}).get("chunk_size", 1000)
        self.CHUNK_OVERLAP = self.config.get("document", {}).get("chunk_overlap", 200)
        self.SUPPORTED_FORMATS = self.config.get("document", {}).get("supported_formats", [".pdf", ".txt", ".docx", ".md"])
        
        # 路径配置
        self.UPLOAD_DIR = self.config.get("paths", {}).get("upload_dir", "./data/uploads")
        
        # 确保目录存在
        os.makedirs(self.VECTOR_DB_DIR, exist_ok=True)
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)

    def _load_config(self):
        if not os.path.exists(self.config_path):
            # 如果找不到配置文件，返回默认空字典或抛出错误
            # 这里为了健壮性，返回空字典，依赖默认值
            return {}
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

# 单例模式
settings = Config()

