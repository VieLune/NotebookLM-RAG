from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    question: str
    history: Optional[List[dict]] = None

class SourceDocument(BaseModel):
    source: str
    page: Optional[int] = None
    content: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]
    
class DocumentResponse(BaseModel):
    filename: str
    status: str
    chunks: int

