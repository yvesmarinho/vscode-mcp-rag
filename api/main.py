"""
FastAPI Qdrant RAG Server
Centralized API for multiple projects to consume Qdrant vector search
without needing individual server.py files.
"""

import os
import logging
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient
from qdrant_client.http import models as qm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables for embeddings and client
embeddings_instance = None
qdrant_client = None

# -------------------- Embeddings Classes --------------------
class Embeddings:
    def __init__(self):
        self.provider = os.getenv("EMBEDDINGS_PROVIDER", "fastembed").lower()
        self.model_name = os.getenv("MODEL_NAME", "BAAI/bge-small-en-v1.5")
        self._model = None
        self._fe_model = None

        if self.provider == "openai":
            try:
                from openai import OpenAI
                self._client = OpenAI()
                self.openai_model = os.getenv(
                    "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
                )
            except ImportError as e:
                raise ImportError(
                    "Package 'openai' not installed. Install with: "
                    "pip install openai"
                ) from e
        elif self.provider == "sentence-transformers":
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except ImportError as e:
                raise ImportError(
                    "Package 'sentence-transformers' not installed. "
                    "Install with: pip install sentence-transformers"
                ) from e
        else:  # fastembed
            try:
                # Try new API first
                try:
                    from fastembed import TextEmbedding
                    self._fe_model = TextEmbedding(model_name=self.model_name)
                except (ImportError, AttributeError):
                    # Fallback to older API
                    from fastembed.embedding import DefaultEmbedding
                    self._fe_model = DefaultEmbedding(model_name=self.model_name)
            except ImportError as e:
                raise ImportError(
                    "Package 'fastembed' not installed. "
                    "Install with: pip install fastembed"
                ) from e

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        if self.provider == "openai":
            resp = self._client.embeddings.create(
                input=texts, model=self.openai_model
            )
            return [d.embedding for d in resp.data]
        elif self.provider == "sentence-transformers":
            vecs = self._model.encode(texts, convert_to_numpy=True)
            return vecs.tolist()
        else:  # fastembed
            vecs = list(self._fe_model.embed(texts))
            return [vec.tolist() for vec in vecs]

# -------------------- Pydantic Models --------------------
class QueryRequest(BaseModel):
    text: str = Field(..., description="Text to search for")
    collection: str = Field("project_docs", description="Collection name")
    top_k: int = Field(5, description="Number of results to return")
    path_prefix: Optional[str] = Field(None, description="Filter by path prefix")
    project_id: Optional[str] = Field(None, description="Project identifier")

class IngestRequest(BaseModel):
    directory: str = Field(..., description="Directory to ingest")
    collection: str = Field("project_docs", description="Collection name")
    project_id: Optional[str] = Field(None, description="Project identifier")
    file_extensions: List[str] = Field(
        [".md", ".txt", ".py", ".js", ".ts", ".json", ".yaml", ".yml"],
        description="File extensions to include"
    )

class DocumentResponse(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any]
    score: float

class QueryResponse(BaseModel):
    results: List[DocumentResponse]
    total: int
    query: str
    collection: str

class CollectionInfo(BaseModel):
    name: str
    vectors_count: int
    points_count: int
    status: str

# -------------------- Startup/Shutdown --------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize global resources on startup."""
    global embeddings_instance, qdrant_client
    
    logger.info("🚀 Starting FastAPI Qdrant RAG Server...")
    
    # Initialize Qdrant client
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_key = os.getenv("QDRANT_API_KEY")
    
    if qdrant_key:
        qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_key)
    else:
        qdrant_client = QdrantClient(url=qdrant_url)
    
    logger.info(f"✅ Connected to Qdrant at {qdrant_url}")
    
    # Initialize embeddings
    embeddings_instance = Embeddings()
    logger.info(f"✅ Embeddings ready: {embeddings_instance.provider}")
    
    yield
    
    logger.info("🛑 Shutting down FastAPI Qdrant RAG Server...")

# -------------------- FastAPI App --------------------
app = FastAPI(
    title="Qdrant RAG API",
    description="Centralized API for vector search across multiple projects",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- Helper Functions --------------------
def ensure_collection_exists(collection_name: str, vector_size: int = 384):
    """Ensure collection exists, create if it doesn't."""
    try:
        qdrant_client.get_collection(collection_name)
        logger.info(f"Collection '{collection_name}' already exists")
    except Exception:
        logger.info(f"Creating collection '{collection_name}'...")
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=qm.VectorParams(
                size=vector_size,
                distance=qm.Distance.COSINE
            )
        )
        logger.info(f"✅ Collection '{collection_name}' created")

def ingest_directory(directory: str, collection: str, project_id: str = None,
                    file_extensions: List[str] = None) -> Dict[str, Any]:
    """Ingest all files from a directory into Qdrant."""
    if file_extensions is None:
        file_extensions = [".md", ".txt", ".py", ".js", ".ts", ".json", ".yaml", ".yml"]
    
    directory_path = Path(directory)
    if not directory_path.exists():
        raise HTTPException(status_code=404, detail=f"Directory not found: {directory}")
    
    files_processed = 0
    points_added = 0
    
    # Collect all files
    all_files = []
    for ext in file_extensions:
        all_files.extend(directory_path.rglob(f"*{ext}"))
    
    if not all_files:
        raise HTTPException(
            status_code=404, 
            detail=f"No files found with extensions {file_extensions}"
        )
    
    # Process files in batches
    batch_size = 100
    batch_docs = []
    batch_ids = []
    batch_metadata = []
    
    for file_path in all_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if len(content.strip()) == 0:
                continue
                
            doc_id = str(uuid.uuid4())
            metadata = {
                "file_path": str(file_path.relative_to(directory_path)),
                "full_path": str(file_path),
                "file_extension": file_path.suffix,
                "file_size": file_path.stat().st_size,
                "project_id": project_id or "default"
            }
            
            batch_docs.append(content)
            batch_ids.append(doc_id)
            batch_metadata.append(metadata)
            files_processed += 1
            
            # Process batch when full
            if len(batch_docs) >= batch_size:
                vectors = embeddings_instance.embed(batch_docs)
                
                points = [
                    qm.PointStruct(
                        id=batch_ids[i],
                        vector=vectors[i],
                        payload=batch_metadata[i]
                    )
                    for i in range(len(batch_docs))
                ]
                
                qdrant_client.upsert(
                    collection_name=collection,
                    points=points
                )
                
                points_added += len(points)
                logger.info(f"Added batch of {len(points)} points to {collection}")
                
                # Reset batch
                batch_docs = []
                batch_ids = []
                batch_metadata = []
        
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            continue
    
    # Process remaining batch
    if batch_docs:
        vectors = embeddings_instance.embed(batch_docs)
        
        points = [
            qm.PointStruct(
                id=batch_ids[i],
                vector=vectors[i],
                payload=batch_metadata[i]
            )
            for i in range(len(batch_docs))
        ]
        
        qdrant_client.upsert(
            collection_name=collection,
            points=points
        )
        
        points_added += len(points)
        logger.info(f"Added final batch of {len(points)} points to {collection}")
    
    return {
        "files_processed": files_processed,
        "points_added": points_added,
        "collection": collection,
        "directory": directory
    }

# -------------------- API Endpoints --------------------
@app.get("/")
async def root():
    """API health check."""
    return {"message": "Qdrant RAG API is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check."""
    try:
        # Check Qdrant connection
        collections = qdrant_client.get_collections()
        qdrant_status = "healthy"
    except Exception as e:
        qdrant_status = f"error: {str(e)}"
    
    return {
        "api": "healthy",
        "qdrant": qdrant_status,
        "embeddings": embeddings_instance.provider if embeddings_instance else "not initialized"
    }

@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Search for documents using semantic similarity."""
    try:
        # Ensure collection exists
        ensure_collection_exists(request.collection)
        
        # Generate embedding for query
        query_vector = embeddings_instance.embed([request.text])[0]
        
        # Build search filter
        search_filter = None
        if request.path_prefix or request.project_id:
            must_conditions = []
            if request.path_prefix:
                must_conditions.append(
                    qm.FieldCondition(
                        key="file_path",
                        match=qm.MatchText(text=request.path_prefix)
                    )
                )
            if request.project_id:
                must_conditions.append(
                    qm.FieldCondition(
                        key="project_id",
                        match=qm.MatchValue(value=request.project_id)
                    )
                )
            search_filter = qm.Filter(must=must_conditions)
        
        # Search in Qdrant
        search_result = qdrant_client.search(
            collection_name=request.collection,
            query_vector=query_vector,
            limit=request.top_k,
            query_filter=search_filter,
            with_payload=True
        )
        
        # Format results
        results = [
            DocumentResponse(
                id=str(point.id),
                content=point.payload.get("content", ""),
                metadata=point.payload,
                score=point.score
            )
            for point in search_result
        ]
        
        return QueryResponse(
            results=results,
            total=len(results),
            query=request.text,
            collection=request.collection
        )
        
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
async def ingest_documents(request: IngestRequest, background_tasks: BackgroundTasks):
    """Ingest documents from a directory into Qdrant."""
    try:
        # Ensure collection exists
        ensure_collection_exists(request.collection)
        
        # Add ingestion task to background
        background_tasks.add_task(
            ingest_directory,
            request.directory,
            request.collection,
            request.project_id,
            request.file_extensions
        )
        
        return {
            "message": "Ingestion started",
            "directory": request.directory,
            "collection": request.collection,
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Ingest error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest/sync")
async def ingest_documents_sync(request: IngestRequest):
    """Ingest documents synchronously (wait for completion)."""
    try:
        # Ensure collection exists
        ensure_collection_exists(request.collection)
        
        # Ingest documents
        result = ingest_directory(
            request.directory,
            request.collection,
            request.project_id,
            request.file_extensions
        )
        
        return {
            "message": "Ingestion completed",
            **result,
            "status": "completed"
        }
        
    except Exception as e:
        logger.error(f"Sync ingest error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/collections", response_model=List[CollectionInfo])
async def list_collections():
    """List all collections with their statistics."""
    try:
        collections_response = qdrant_client.get_collections()
        collections_info = []
        
        for collection in collections_response.collections:
            try:
                collection_info = qdrant_client.get_collection(collection.name)
                collections_info.append(
                    CollectionInfo(
                        name=collection.name,
                        vectors_count=collection_info.vectors_count or 0,
                        points_count=collection_info.points_count or 0,
                        status="active"
                    )
                )
            except Exception as e:
                collections_info.append(
                    CollectionInfo(
                        name=collection.name,
                        vectors_count=0,
                        points_count=0,
                        status=f"error: {str(e)}"
                    )
                )
        
        return collections_info
        
    except Exception as e:
        logger.error(f"Collections list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/collections/{collection_name}")
async def delete_collection(collection_name: str):
    """Delete a collection and all its data."""
    try:
        qdrant_client.delete_collection(collection_name)
        return {"message": f"Collection '{collection_name}' deleted successfully"}
        
    except Exception as e:
        logger.error(f"Delete collection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/collections/{collection_name}/stats")
async def get_collection_stats(collection_name: str):
    """Get detailed statistics for a specific collection."""
    try:
        collection_info = qdrant_client.get_collection(collection_name)
        
        return {
            "name": collection_name,
            "vectors_count": collection_info.vectors_count,
            "points_count": collection_info.points_count,
            "status": collection_info.status,
            "config": {
                "vector_size": collection_info.config.params.vectors.size,
                "distance": collection_info.config.params.vectors.distance,
            }
        }
        
    except Exception as e:
        logger.error(f"Collection stats error: {e}")
        raise HTTPException(status_code=404, detail=f"Collection '{collection_name}' not found")

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    logger.info(f"🚀 Starting server on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )