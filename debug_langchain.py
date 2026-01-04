import sys
import importlib

print(f"Python Executable: {sys.executable}")

try:
    import langchain
    print(f"LangChain Version: {langchain.__version__}")
    print(f"LangChain Path: {langchain.__file__}")
except ImportError as e:
    print(f"Error importing langchain: {e}")

try:
    from langchain.chains import create_retrieval_chain
    print("Successfully imported create_retrieval_chain")
except ImportError as e:
    print(f"Error importing create_retrieval_chain: {e}")
except Exception as e:
    print(f"Other error: {e}")

