from fastapi import APIRouter, HTTPException
from app.services.chat_service import ChatService
from app.api.schemas import ChatRequest, ChatResponse, SourceDocument

router = APIRouter()
chat_service = ChatService()

@router.post("/query", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = chat_service.chat(request.question)
        
        sources = []
        for doc in response["source_documents"]:
            sources.append(SourceDocument(
                source=doc.metadata.get("source", "unknown"),
                page=doc.metadata.get("page", None),
                content=doc.page_content
            ))
            
        return ChatResponse(
            answer=response["answer"],
            sources=sources
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

