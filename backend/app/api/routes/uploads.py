from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from app.core.config import get_settings, Settings
from app.core.dependencies import validate_image_file, get_upload_path
import os
from uuid import uuid4

router = APIRouter()

@router.post("/image")
async def upload_image(
    file: UploadFile = Depends(validate_image_file),
    upload_path: str = Depends(get_upload_path),
    settings: Settings = Depends(get_settings)
):
    """
    Upload image file and return public URL.
    Validates file type, size, and content.
    """
    try:
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1].lower()
        unique_filename = f"{uuid4().hex}{file_extension}"
        file_path = os.path.join(upload_path, unique_filename)
        
        # Security: Ensure path is within upload directory
        real_upload_path = os.path.realpath(upload_path)
        real_file_path = os.path.realpath(file_path)
        if not real_file_path.startswith(real_upload_path):
            raise HTTPException(status_code=400, detail="Invalid file path")
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Return public URL
        # In production, this should be your CDN or public URL
        public_url = f"http://localhost:8000/uploads/{unique_filename}"
        
        return {
            "url": public_url,
            "filename": unique_filename,
            "size": len(content)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to upload file: {str(e)}"
        )
