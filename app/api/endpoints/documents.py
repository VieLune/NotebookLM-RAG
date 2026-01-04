import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from app.core.config import settings
from app.services.chat_service import ChatService
from app.api.schemas import DocumentResponse

router = APIRouter()
chat_service = ChatService() # 注意：这里每次请求可能会重新实例化，生产环境应该用 Depends 注入单例

@router.post("/upload", response_model=List[DocumentResponse])
async def upload_documents(files: List[UploadFile] = File(...)):
    results = []
    temp_paths = []
    
    try:
        # 1. 保存文件
        for file in files:
            file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            temp_paths.append(file_path)
            
        # 2. 处理文件
        # 注意：这里简化处理，直接调用 service。如果是大文件，应该用 BackgroundTasks
        chat_service.process_and_index_files(temp_paths)
        
        for path in temp_paths:
            results.append(DocumentResponse(
                filename=os.path.basename(path),
                status="processed",
                chunks=0 # service 没返回单个文件的 chunk 数，这里简化
            ))
            
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

