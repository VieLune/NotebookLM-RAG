# GeminiDocAgent

GeminiDocAgent 是一个基于 Google Gemini API 和 LangChain 的智能文档分析 Agent，旨在提供类似 NotebookLM 的文档问答和分析体验。

## 快速开始

### 1. 环境准备

**使用 Conda (推荐)**:

```bash
conda env create -f environment.yml
conda activate gemini-doc-agent
```

**或者使用 pip**:

确保安装 Python 3.9+。

```bash
pip install -r requirements.txt
```

### 2. 配置

复制环境变量模板并填写你的 Gemini API Key：

```bash
cp .env.example .env
# 编辑 .env 文件填入 GEMINI_API_KEY
```

配置文件位于 `config.yaml`，通常无需修改即可运行。

### 3. 运行服务

#### 启动后端 API

```bash
python main.py
```

API 将在 `http://localhost:8000` 运行。

#### 启动 Streamlit 界面 (开发中)

```bash
streamlit run streamlit_app.py
```

## 项目结构

- `app/`: 核心代码
  - `services/`: 业务逻辑 (文档处理, 向量存储, LLM)
  - `api/`: FastAPI 路由
  - `core/`: 配置管理
- `data/`: 数据存储 (文档上传, 向量库)

