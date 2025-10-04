from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class PDFUploadResponse(BaseModel):
    success: bool = Field(..., description="Whether the upload was successful")
    message: str = Field(..., description="Response message")
    filename: str = Field(..., description="Original filename")
    saved_filename: str = Field(..., description="Saved filename with timestamp")
    file_size: int = Field(..., description="File size in bytes")
    file_path: str = Field(..., description="Path where file is saved")
    processing_result: Optional[Dict[str, Any]] = Field(None, description="Results from PDF processing")

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error message")
