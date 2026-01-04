# MiniNotebookLM

基于 Python (Conda环境)、LangChain 和 Gemini API 的 RAG 应用，类似 NotebookLM。

## 环境设置

### 1. 创建 Conda 环境

使用项目提供的 `environment.yml` 文件创建 Conda 环境：

```bash
conda env create -f environment.yml
```

### 2. 激活环境

**Windows (CMD):**
```bash
conda activate notebooklm-rag
```

**Windows (PowerShell):**
```powershell
conda activate notebooklm-rag
```

**Linux/macOS:**
```bash
conda activate notebooklm-rag
```

### 3. 配置环境变量

1. 复制 `env.example` 文件为 `.env`：
   ```bash
   copy env.example .env
   ```
   (Linux/macOS 使用: `cp env.example .env`)

2. 编辑 `.env` 文件，填入您的 Google Gemini API Key：
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

### 4. 运行 Streamlit 应用

在激活的 Conda 环境中运行：

```bash
streamlit run main.py
```

应用将在浏览器中自动打开，默认地址为 `http://localhost:8501`

## 项目结构

```
MiniNotebookLM/
├── environment.yml      # Conda 环境配置
├── env.example         # 环境变量示例
├── .env                # 环境变量（需自行创建）
├── main.py             # Streamlit 应用入口
├── rag_engine.py       # RAG 引擎类
└── README.md           # 项目说明
```

## 依赖说明

- **langchain**: LangChain 核心库
- **langchain-google-genai**: Google Gemini 集成
- **langchain-community**: LangChain 社区扩展
- **chromadb**: 向量数据库
- **pypdf**: PDF 文档处理
- **streamlit**: Web 应用框架
- **python-dotenv**: 环境变量管理
- **watchdogs**: Streamlit 文件监控依赖

