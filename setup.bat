@echo off
REM MiniNotebookLM 环境设置脚本 (Windows)

echo ========================================
echo MiniNotebookLM 环境设置
echo ========================================
echo.

echo [1/3] 创建 Conda 环境...
conda env create -f environment.yml
if %errorlevel% neq 0 (
    echo 错误: Conda 环境创建失败
    pause
    exit /b 1
)

echo.
echo [2/3] 激活环境...
call conda activate notebooklm-rag
if %errorlevel% neq 0 (
    echo 错误: 环境激活失败
    pause
    exit /b 1
)

echo.
echo [3/3] 复制环境变量示例文件...
if not exist .env (
    copy env.example .env
    echo 已创建 .env 文件，请编辑并填入您的 GOOGLE_API_KEY
) else (
    echo .env 文件已存在，跳过
)

echo.
echo ========================================
echo 设置完成！
echo ========================================
echo.
echo 下一步：
echo 1. 编辑 .env 文件，填入您的 GOOGLE_API_KEY
echo 2. 运行: streamlit run main.py
echo.
pause

