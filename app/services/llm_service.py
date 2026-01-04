from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings

class LLMService:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set")

        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            temperature=settings.GEMINI_TEMPERATURE,
            max_tokens=settings.GEMINI_MAX_TOKENS,
            google_api_key=settings.GEMINI_API_KEY,
            convert_system_message_to_human=True # Gemini 早期版本有时需要这个
        )

    def get_llm(self):
        return self.llm

