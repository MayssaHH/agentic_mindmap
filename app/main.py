from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import endpoints

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

# Include routers
app.include_router(endpoints.router, prefix="/api", tags=["PDF Processing"])

@app.get("/")
async def root():
    return {"message": "Agentic Mindmap API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}