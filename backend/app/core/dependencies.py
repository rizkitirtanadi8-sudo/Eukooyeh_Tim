"""
FastAPI dependencies untuk dependency injection.
"""
from fastapi import Depends, HTTPException, UploadFile
from app.core.config import Settings, get_settings
import os


def get_upload_path(settings: Settings = Depends(get_settings)) -> str:
    """Ensure upload directory exists."""
    os.makedirs(settings.upload_dir, exist_ok=True)
    return settings.upload_dir


async def validate_image_file(file: UploadFile) -> UploadFile:
    """
    Validate uploaded file adalah image dengan format yang valid.
    
    Args:
        file: Uploaded file dari request
        
    Returns:
        UploadFile jika valid
        
    Raises:
        HTTPException: Jika file tidak valid
    """
    from PIL import Image
    import io
    
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
    allowed_extensions = [".jpg", ".jpeg", ".png", ".webp"]
    
    # Check filename
    filename = file.filename or ""
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    # Check for path traversal attempts
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    # Check by file extension
    extension = filename.lower().split('.')[-1] if '.' in filename else ""
    extension_valid = f".{extension}" in allowed_extensions
    
    # Check by content type
    content_type_valid = file.content_type in allowed_types
    
    # Must have valid extension
    if not extension_valid:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed extensions: {', '.join(allowed_extensions)}"
        )
    
    # Validate actual image content (prevent fake extensions)
    try:
        content = await file.read()
        
        # Check file size (max 10MB)
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Max 10MB")
        
        # Validate it's actually an image
        img = Image.open(io.BytesIO(content))
        img.verify()  # Verify it's a valid image
        
        # Reset file pointer for later use
        await file.seek(0)
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image file: {str(e)}"
        )
    
    return file
