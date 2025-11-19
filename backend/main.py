"""
FastAPI Backend for Jira Sense
Provides REST API endpoints for ChromaDB operations
Banking-compliant: All processing runs locally
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.data_loader import JiraDataLoader
from core.search_builder import JiraSearchBuilder

# Initialize FastAPI app
app = FastAPI(
    title="Jira Sense API",
    description="Banking-compliant search API for Jira data using ChromaDB and sentence-transformers",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
DB_PATH = "./temp/chromadb"
COLLECTION_NAME = "jira_content"
MODEL_NAME = "all-MiniLM-L6-v2"

# Global instances (initialized on startup)
data_loader: Optional[JiraDataLoader] = None
search_builder: Optional[JiraSearchBuilder] = None


# Pydantic Models
class BuildRequest(BaseModel):
    """Request model for building ChromaDB from CSV"""
    csv_path: str = Field(..., description="Path to CSV file", example="./temp/files/chunked_data.csv")
    model_name: Optional[str] = Field(MODEL_NAME, description="Sentence transformer model name")
    batch_size: Optional[int] = Field(100, description="Batch size for processing")


class SearchRequest(BaseModel):
    """Request model for searching ChromaDB"""
    keyword: str = Field(..., description="Search keyword", example="Mobile no")
    n_results: Optional[int] = Field(50, description="Maximum number of results to return")
    case_sensitive: Optional[bool] = Field(False, description="Whether search is case-sensitive")
    country: Optional[str] = Field(None, description="Filter by country", example="Singapore")
    content_type: Optional[str] = Field(None, description="Filter by content type", example="validation")


class SearchResponse(BaseModel):
    """Response model for search results"""
    total_results: int
    results: List[Dict[str, Any]]
    message: str


class BuildResponse(BaseModel):
    """Response model for build operation"""
    status: str
    total_documents: int
    collection_name: str
    model_name: str
    message: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str
    db_connected: bool
    total_documents: int


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize ChromaDB connections on startup"""
    global data_loader, search_builder
    
    try:
        # Initialize data loader
        data_loader = JiraDataLoader(
            db_path=DB_PATH,
            collection_name=COLLECTION_NAME,
            model_name=MODEL_NAME
        )
        
        # Initialize search builder
        search_builder = JiraSearchBuilder(
            db_path=DB_PATH,
            collection_name=COLLECTION_NAME,
            model_name=MODEL_NAME
        )
        
        print("✅ FastAPI backend initialized successfully")
        print(f"✅ Using model: {MODEL_NAME} (banking-compliant)")
        
    except Exception as e:
        print(f"⚠️  Warning: Could not initialize search builder: {e}")
        print("ℹ️  Build the database first using /api/build endpoint")


# Routes

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "Jira Sense API - Banking Compliant",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        if search_builder is None:
            return HealthResponse(
                status="warning",
                message="Search builder not initialized. Build database first.",
                db_connected=False,
                total_documents=0
            )
        
        info = search_builder.get_all_data()
        total_docs = len(info.get('ids', []))
        
        return HealthResponse(
            status="healthy",
            message="API is running and database is connected",
            db_connected=True,
            total_documents=total_docs
        )
    except Exception as e:
        return HealthResponse(
            status="error",
            message=f"Health check failed: {str(e)}",
            db_connected=False,
            total_documents=0
        )


@app.post("/api/build", response_model=BuildResponse)
async def build_database(request: BuildRequest):
    """
    Build ChromaDB from CSV file
    
    This endpoint:
    1. Reads CSV data from specified path
    2. Generates embeddings using sentence-transformers (local, banking-compliant)
    3. Stores data in ChromaDB
    
    **Banking Compliance**: All processing happens locally, no external API calls
    """
    global data_loader, search_builder
    
    try:
        # Check if CSV file exists
        if not os.path.exists(request.csv_path):
            raise HTTPException(
                status_code=404,
                detail=f"CSV file not found at: {request.csv_path}"
            )
        
        # Initialize or reinitialize data loader with specified model
        data_loader = JiraDataLoader(
            db_path=DB_PATH,
            collection_name=COLLECTION_NAME,
            model_name=request.model_name or MODEL_NAME
        )
        
        # Load data from CSV
        result = data_loader.load_from_csv(
            csv_path=request.csv_path,
            batch_size=request.batch_size
        )
        
        # Reinitialize search builder after loading data
        search_builder = JiraSearchBuilder(
            db_path=DB_PATH,
            collection_name=COLLECTION_NAME,
            model_name=request.model_name or MODEL_NAME
        )
        
        if result.get('status') == 'success':
            return BuildResponse(
                status="success",
                total_documents=result['total_loaded'],
                collection_name=COLLECTION_NAME,
                model_name=request.model_name or MODEL_NAME,
                message=f"Successfully loaded {result['total_loaded']} documents into ChromaDB"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to load data: {result.get('message', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error building database: {str(e)}"
        )


@app.post("/api/search", response_model=SearchResponse)
async def search_data(request: SearchRequest):
    """
    Search ChromaDB by keyword (case-insensitive)
    
    This endpoint:
    1. Takes a search keyword
    2. Performs semantic search using local embeddings
    3. Filters results with case-insensitive keyword matching
    4. Returns matched documents with metadata
    
    **Examples:**
    - "Mobile no" matches: mobile no, Mobile Number, MOBILE NO, mobile_no
    - "email address" matches: Email Address, e-mail address, EMAIL ADDRESS
    
    **Banking Compliance**: All processing happens locally, no external API calls
    """
    if search_builder is None:
        raise HTTPException(
            status_code=503,
            detail="Search builder not initialized. Please build the database first using /api/build endpoint"
        )
    
    try:
        # Build filter conditions
        where_filter = None
        if request.country or request.content_type:
            where_filter = {}
            if request.country:
                where_filter["country"] = request.country
            if request.content_type:
                where_filter["content_type"] = request.content_type
        
        # Perform search
        results = search_builder.search_by_keyword(
            keyword=request.keyword,
            n_results=request.n_results,
            where=where_filter,
            case_sensitive=request.case_sensitive
        )
        
        return SearchResponse(
            total_results=len(results),
            results=results,
            message=f"Found {len(results)} matching documents for keyword: '{request.keyword}'"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching data: {str(e)}"
        )


@app.get("/api/search/keyword/{keyword}", response_model=SearchResponse)
async def search_by_keyword_get(
    keyword: str,
    n_results: int = Query(50, description="Maximum number of results"),
    case_sensitive: bool = Query(False, description="Case-sensitive search"),
    country: Optional[str] = Query(None, description="Filter by country"),
    content_type: Optional[str] = Query(None, description="Filter by content type")
):
    """
    Search ChromaDB by keyword using GET method (case-insensitive)
    
    **Example**: `/api/search/keyword/Mobile%20no?n_results=10&country=Singapore`
    
    **Banking Compliance**: All processing happens locally, no external API calls
    """
    if search_builder is None:
        raise HTTPException(
            status_code=503,
            detail="Search builder not initialized. Please build the database first using /api/build endpoint"
        )
    
    try:
        # Build filter conditions
        where_filter = None
        if country or content_type:
            where_filter = {}
            if country:
                where_filter["country"] = country
            if content_type:
                where_filter["content_type"] = content_type
        
        # Perform search
        results = search_builder.search_by_keyword(
            keyword=keyword,
            n_results=n_results,
            where=where_filter,
            case_sensitive=case_sensitive
        )
        
        return SearchResponse(
            total_results=len(results),
            results=results,
            message=f"Found {len(results)} matching documents for keyword: '{keyword}'"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching data: {str(e)}"
        )


@app.get("/api/collection/info")
async def get_collection_info():
    """Get information about the current ChromaDB collection"""
    if data_loader is None:
        raise HTTPException(
            status_code=503,
            detail="Data loader not initialized"
        )
    
    try:
        info = data_loader.get_collection_info()
        return {
            "status": "success",
            "collection_name": info['collection_name'],
            "total_documents": info['total_documents'],
            "metadata": info.get('metadata', {}),
            "model": MODEL_NAME,
            "banking_compliant": True
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting collection info: {str(e)}"
        )


@app.get("/api/collection/all")
async def get_all_documents():
    """Get all documents from the collection"""
    if search_builder is None:
        raise HTTPException(
            status_code=503,
            detail="Search builder not initialized"
        )
    
    try:
        all_data = search_builder.get_all_data()
        return {
            "status": "success",
            "total_documents": len(all_data.get('ids', [])),
            "data": all_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting all documents: {str(e)}"
        )


# Run with: uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
