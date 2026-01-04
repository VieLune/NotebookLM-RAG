from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json
from app.services.chat_service import ChatService
from app.api.schemas import ChatRequest, ChatResponse, SourceDocument

router = APIRouter()
chat_service = ChatService()

@router.post("/query", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = chat_service.chat(request.question, chat_history=request.history)
        
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

@router.post("/stream")
async def chat_stream(request: ChatRequest):
    def generate():
        try:
            for chunk in chat_service.chat_stream(request.question, chat_history=request.history):
                if chunk["type"] == "source":
                    # Serialize source documents
                    sources_data = []
                    for doc in chunk["content"]:
                        sources_data.append({
                            "source": doc.metadata.get("source", "unknown"),
                            "page": doc.metadata.get("page", None),
                            "content": doc.page_content
                        })
                    yield json.dumps({"type": "source", "content": sources_data}, ensure_ascii=False) + "\n"
                else:
                    # Yield answer chunk
                    yield json.dumps(chunk, ensure_ascii=False) + "\n"
        except Exception as e:
            yield json.dumps({"type": "error", "content": str(e)}, ensure_ascii=False) + "\n"

    return StreamingResponse(generate(), media_type="application/x-ndjson")

