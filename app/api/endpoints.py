from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional
import aiofiles
import os
from pathlib import Path
from datetime import datetime

from app.core.models import PDFUploadResponse, ErrorResponse
from app.services.pdf_processor import PDFProcessor

router = APIRouter()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Maximum file size (e.g., 50MB)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB in bytes

@router.post(
    "/upload-pdf",
    response_model=PDFUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload a PDF file for processing",
    description="Upload a PDF file containing slides for processing and analysis"
)
async def upload_pdf(
    file: UploadFile = File(..., description="PDF file to upload")
):
    """
    Upload a PDF file for processing.
    
    - **file**: PDF file (max 50MB)
    
    Returns processing results and file information.
    """
    
    # Validate file type
    if not file.content_type == "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Validate filename
    if not file.filename or not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid PDF filename"
        )
    
    try:
        # Read file content
        contents = await file.read()
        file_size = len(contents)
        
        # Validate file size
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file uploaded"
            )
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = UPLOAD_DIR / safe_filename
        
        # Save file asynchronously
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(contents)
        
        # Process the PDF
        processor = PDFProcessor()
        processing_result = await processor.process_pdf(file_path)
        
        return PDFUploadResponse(
            success=True,
            message="PDF uploaded and processed successfully",
            filename=file.filename,
            saved_filename=safe_filename,
            file_size=file_size,
            file_path=str(file_path),
            processing_result=processing_result
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Clean up file if it was saved
        if 'file_path' in locals() and file_path.exists():
            os.remove(file_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing PDF: {str(e)}"
        )
    finally:
        await file.close()


@router.delete(
    "/delete-pdf/{filename}",
    status_code=status.HTTP_200_OK,
    summary="Delete an uploaded PDF file"
)
async def delete_pdf(filename: str):
    """
    Delete a previously uploaded PDF file.
    
    - **filename**: Name of the saved file to delete
    """
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    try:
        os.remove(file_path)
        return {"success": True, "message": f"File {filename} deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting file: {str(e)}"
        )
