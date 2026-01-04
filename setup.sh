#!/bin/bash
# MiniNotebookLM 环境设置脚本 (Linux/macOS)

echo "========================================"
echo "MiniNotebookLM 环境设置"
echo "========================================"
echo ""

echo "[1/3] 创建 Conda 环境..."
conda env create -f environment.yml
if [ $? -ne 0 ]; then
    echo "错误: Conda 环境创建失败"
    exit 1
fi

echo ""
echo "[2/3] 激活环境..."
echo "请手动运行: conda activate notebooklm-rag"

echo ""
echo "[3/3] 复制环境变量示例文件..."
if [ ! -f .env ]; then
    cp env.example .env
    echo "已创建 .env 文件，请编辑并填入您的 GOOGLE_API_KEY"
else
    echo ".env 文件已存在，跳过"
fi

echo ""
echo "========================================"
echo "设置完成！"
echo "========================================"
echo ""
echo "下一步："
echo "1. 运行: conda activate notebooklm-rag"
echo "2. 编辑 .env 文件，填入您的 GOOGLE_API_KEY"
echo "3. 运行: streamlit run main.py"
echo ""

