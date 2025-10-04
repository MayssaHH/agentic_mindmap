from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api import endpoints
import os
from pathlib import Path

app = FastAPI(
    title="Agentic Mindmap API",
    description="API for processing PDF slides and creating mindmaps",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(endpoints.router, prefix="/api", tags=["PDF Processing"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Mount static files and serve frontend (for production/Docker)
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    # Mount assets directory
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")
    
    # Catch-all route to serve the SPA
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Skip API routes
        if full_path.startswith("api/"):
            return {"message": "API endpoint not found"}
        
        # Serve specific file if it exists
        file_path = frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        
        # Default to index.html for SPA routing
        return FileResponse(frontend_dist / "index.html")
else:
    @app.get("/")
    async def root():
        return {"message": "Agentic Mindmap API is running (frontend not built)"}