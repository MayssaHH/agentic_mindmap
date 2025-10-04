from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class GraphNode(BaseModel):
    id: str = Field(..., description="Node ID")
    title: str = Field(..., description="Node title")
    type: str = Field(..., description="Node type (central or subnode)")

class GraphEdge(BaseModel):
    id: str = Field(..., description="Edge ID")
    from_node: str = Field(..., alias="from", description="Source node ID")
    to_node: str = Field(..., alias="to", description="Target node ID")
    label: str = Field(..., description="Edge label")
    
    class Config:
        populate_by_name = True

class GraphData(BaseModel):
    nodes: List[GraphNode] = Field(default_factory=list, description="List of graph nodes")
    edges: List[GraphEdge] = Field(default_factory=list, description="List of graph edges")

class ProcessingMetadata(BaseModel):
    thread_id: str = Field(..., description="Processing session ID")
    total_pages: int = Field(..., description="Total pages in PDF")
    total_topics: int = Field(..., description="Total topics identified")
    total_nodes: int = Field(..., description="Total nodes in graph")
    total_edges: int = Field(..., description="Total edges in graph")
    export_file_path: str = Field(default="", description="Path to exported detailed results")

class TopicInfo(BaseModel):
    topic_title: str = Field(..., description="Topic title")
    slide_numbers: List[int] = Field(..., description="Slide numbers for this topic")
    summaries: List[str] = Field(..., description="Summaries of slides in this topic")

class PDFProcessingResult(BaseModel):
    graph: GraphData = Field(..., description="Mind map graph data")
    metadata: ProcessingMetadata = Field(..., description="Processing metadata")
    topics: List[TopicInfo] = Field(default_factory=list, description="Topic information")

class PDFUploadResponse(BaseModel):
    success: bool = Field(..., description="Whether the upload was successful")
    message: str = Field(..., description="Response message")
    filename: str = Field(..., description="Original filename")
    saved_filename: str = Field(..., description="Saved filename with timestamp")
    file_size: int = Field(..., description="File size in bytes")
    file_path: str = Field(..., description="Path where file is saved")
    processing_result: Optional[PDFProcessingResult] = Field(None, description="Results from PDF processing")

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error message")
