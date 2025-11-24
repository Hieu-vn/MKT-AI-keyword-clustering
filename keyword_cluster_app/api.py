import json
import logging
import logging.handlers
import os
import sys
from typing import Any, Dict, List, Optional
from uuid import uuid4

from arq import ArqRedis
from arq.connections import RedisSettings
from fastapi import Body, FastAPI, HTTPException, Request, status, Security, Depends
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from keyword_cluster_app.config import LOG_FILE_PATH, REDIS_URL, SYNC_MAX_KEYWORDS, ASYNC_MAX_KEYWORDS, API_KEY
from keyword_cluster_app.model import load_model, model
from keyword_cluster_app.model import load_model, model
from keyword_cluster_app.services.clustering_service import ClusteringService

# Configure logging for the API
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.handlers.RotatingFileHandler(
            LOG_FILE_PATH, maxBytes=10*1024*1024, backupCount=5
        )
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Keyword Clustering API",
    description="API for semantic keyword clustering and analysis.",
    version="1.0.0",
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# --- CORS Configuration ---
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development. Restrict in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Health Check ---
@app.get("/health", tags=["System"])
async def health_check():
    """Check system health status."""
    return {
        "status": "healthy",
        "service": "keyword-clustering-api",
        "version": "2.0.0"
    }

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Load API keys helper
KEYS_FILE = "api_keys.json"

def validate_key_file(api_key: str) -> bool:
    """Check if the API key exists and is active in the keys file"""
    if not os.path.exists(KEYS_FILE):
        # Fallback to env var if no file exists (for backward compatibility)
        return api_key == API_KEY
        
    try:
        with open(KEYS_FILE, 'r') as f:
            data = json.load(f)
            
        if "keys" not in data:
            return False
            
        for k in data["keys"]:
            if k.get("key") == api_key and k.get("active", True):
                return True
        return False
    except Exception as e:
        logger.error(f"Error reading API keys file: {e}")
        return False

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if validate_key_file(api_key_header):
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials",
    )

@app.exception_handler(RateLimitExceeded)
async def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit exceeded: {exc.detail}"},
    )


# Pydantic models for task management
class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    message: Optional[str] = None


class TaskResultResponse(BaseModel):
    task_id: str
    status: str
    progress: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Pydantic models for request and response
class KeywordInput(BaseModel):
    text: str = Field(..., description="The keyword text.")
    volume: Optional[int] = Field(0, description="The search volume for the keyword.")


class KeywordOutput(BaseModel):
    text: str
    volume: int
    matching_point: float = Field(..., description="Similarity score (0-100) to the cluster theme.")
    
    # Hidden advanced fields (calculated internally but not returned by default to simplify view)
    # micro_intent: Optional[str] = None
    # difficulty: Optional[int] = None
    # serp_features: Optional[List[str]] = None
    # is_question: Optional[bool] = None
    # question_type: Optional[str] = None
    # keyword_type: Optional[str] = None
    # commercial_score: Optional[int] = None


class ClusteringRequest(BaseModel):
    keywords: List[KeywordInput] = Field(..., min_items=1, description="List of keywords to cluster.")
    level: str = Field("trung bình", description="Clustering detail level: 'thấp', 'trung bình', 'cao'.")
    min_cluster_size: Optional[int] = Field(None, description="Minimum number of keywords for a cluster.")
    clustering_method: str = Field("semantic", description="Clustering method: 'semantic' or 'serp'.")


class ClusterResult(BaseModel):
    cluster_name: str
    keywords: List[KeywordOutput]
    total_volume_topic: Optional[int] = Field(None, description="Total search volume.")
    
    # Hidden advanced fields
    # cluster_intent: str
    # content_format: Optional[str] = None
    # parent_topic: Optional[str] = None
    # related_keywords: Optional[List[str]] = None
    # avg_commercial_score: Optional[float] = None


class ClusteringResponse(BaseModel):
    clusters: Dict[str, ClusterResult]
    unclustered_keywords: List[KeywordOutput]
    summary: Dict[str, Any]

@app.post("/cluster_keywords_sync", response_model=ClusteringResponse)
@limiter.limit("10/minute")
async def cluster_keywords_sync_endpoint(request: Request, payload: ClusteringRequest = Body(...), api_key: str = Depends(get_api_key)):
    if len(payload.keywords) > SYNC_MAX_KEYWORDS:
        raise HTTPException(400, detail=f"For synchronous processing, a maximum of {SYNC_MAX_KEYWORDS:,} keywords is allowed.")
    
    if model is None:
        raise HTTPException(status_code=503, detail="AI model is not loaded. Please try again later.")

    try:
        logger.info(f"Received synchronous clustering request for {len(payload.keywords)} keywords.")
        
        # Prepare the payload for the processing function
        worker_payload = {
            "raw_keywords_with_volume": [kw.dict() for kw in payload.keywords],
            "level": payload.level,
            "min_cluster_size_override": payload.min_cluster_size,
            "clustering_method": payload.clustering_method,
        }
        
        # Call the clustering function directly
        service = ClusteringService()
        result_data = service.process_clustering(**worker_payload)

        # Convert the raw result to the Pydantic response model
        response_clusters = {}
        for cluster_name, cluster_data in result_data.get("clusters", {}).items():
            response_clusters[cluster_name] = ClusterResult(
                cluster_name=cluster_name,
                keywords=[KeywordOutput(**kw) for kw in cluster_data.get("keywords", [])],
                total_volume_topic=cluster_data.get("total_volume_topic"),
                researched_entities=cluster_data.get("researched_entities", []),
                cluster_intent=cluster_data.get("cluster_intent", ""),
                coherence_score=cluster_data.get("coherence_score"),
                difficulty_score=cluster_data.get("difficulty_score"),
                opportunity_score=cluster_data.get("opportunity_score"),
                llm_name_score=cluster_data.get("llm_name_score"),
                content_type_suggestion=cluster_data.get("content_type_suggestion"),
                llm_summary=cluster_data.get("llm_summary"),
                llm_content_ideas=cluster_data.get("llm_content_ideas"),
            )

        response_unclustered = [KeywordOutput(**kw) for kw in result_data.get("unclustered", [])]
        
        return ClusteringResponse(
            clusters=response_clusters,
            unclustered_keywords=response_unclustered,
            summary=result_data.get("summary", {}),
        )

    except Exception as e:
        logger.exception("Error during synchronous clustering:")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Keyword Clustering API...")
    # set_seed(42) # Seed should be set in worker for reproducibility of tasks
    logger.info("Loading AI model...")
    try:
        load_model()
        if model is None:
            raise RuntimeError("AI model could not be loaded.")
        logger.info("AI model loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load AI model at startup: {e}")
        pass
    
    # Initialize ARQ Redis client
    app.state.arq_redis = await ArqRedis(RedisSettings.from_dsn(REDIS_URL))
    logger.info("ARQ Redis client initialized.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Keyword Clustering API...")
    if hasattr(app.state, 'arq_redis') and app.state.arq_redis:
        await app.state.arq_redis.close()
        logger.info("ARQ Redis client closed.")

@app.post("/cluster_keywords", response_model=TaskStatusResponse, status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("100/minute")  # Tăng lên cho agency dùng thoải mái
async def cluster_keywords_endpoint(request: Request, payload: ClusteringRequest = Body(...), api_key: str = Depends(get_api_key)):
    if len(payload.keywords) > ASYNC_MAX_KEYWORDS:
        raise HTTPException(400, detail=f"Tối đa {ASYNC_MAX_KEYWORDS:,} từ khóa mỗi lần")
    """
    Submits a keyword clustering task to the background queue.
    """
    if model is None:
        raise HTTPException(status_code=503, detail="AI model is not loaded. Please try again later.")

    task_id = str(uuid4())
    logger.info(f"Received clustering request. Assigning task_id: {task_id}")

    # Prepare payload for the worker
    worker_payload = {
        "raw_keywords_with_volume": [kw.dict() for kw in payload.keywords],
        "level": payload.level,
        "min_cluster_size_override": payload.min_cluster_size,
        "clustering_method": payload.clustering_method,
    }

    try:
        # Enqueue the background task
        await app.state.arq_redis.enqueue_job(
            "background_process_clustering",
            task_id,
            worker_payload,
            _job_id=task_id # Use task_id as job_id for easier retrieval
        )
        
        # Store initial status in Redis
        await app.state.arq_redis.set(f"task:{task_id}:status", "pending")
        await app.state.arq_redis.set(f"task:{task_id}:progress", "0%")

        return TaskStatusResponse(
            task_id=task_id,
            status="pending",
            message="Clustering task submitted successfully. Use /results/{task_id} to check status."
        )

    except Exception as e:
        logger.exception(f"Error submitting clustering task {task_id}:")
        raise HTTPException(status_code=500, detail=f"Failed to submit task: {e}")

@app.get("/results/{task_id}", response_model=TaskResultResponse)
async def get_clustering_results(task_id: str):
    """
    Retrieves the status and results of a submitted clustering task.
    """
    arq_redis: ArqRedis = app.state.arq_redis

    status_key = f"task:{task_id}:status"
    progress_key = f"task:{task_id}:progress"
    result_key = f"task:{task_id}:result"
    error_key = f"task:{task_id}:error"

    status_str = await arq_redis.get(status_key)
    progress_str = await arq_redis.get(progress_key)
    error_str = await arq_redis.get(error_key)

    if status_str is None:
        raise HTTPException(status_code=404, detail="Task not found.")

    status_str = status_str.decode('utf-8')
    progress_str = progress_str.decode('utf-8') if progress_str else "0%"

    if status_str == "completed":
        result_json = await arq_redis.get(result_key)
        if result_json:
            result_data = json.loads(result_json.decode('utf-8'))
            # Convert raw results to Pydantic model for validation/consistency
            response_clusters = {}
            for cluster_name, cluster_data in result_data["clusters"].items():
                response_clusters[cluster_name] = ClusterResult(
                    cluster_name=cluster_name,
                    keywords=[KeywordOutput(**kw) for kw in cluster_data["keywords"]],
                    total_volume_topic=cluster_data.get("total_volume_topic"),
                    researched_entities=cluster_data.get("researched_entities", []),
                    cluster_intent=cluster_data.get("cluster_intent", ""),
                    coherence_score=cluster_data.get("coherence_score"),
                    difficulty_score=cluster_data.get("difficulty_score"),
                    opportunity_score=cluster_data.get("opportunity_score"),
                    llm_name_score=cluster_data.get("llm_name_score"),
                    content_type_suggestion=cluster_data.get("content_type_suggestion"),
                    llm_summary=cluster_data.get("llm_summary"),
                    llm_content_ideas=cluster_data.get("llm_content_ideas"),
                )
            
            response_unclustered = [KeywordOutput(**kw) for kw in result_data["unclustered"]]

            final_result = ClusteringResponse(
                clusters=response_clusters,
                unclustered_keywords=response_unclustered,
                summary=result_data["summary"],
            ).dict() # Convert to dict for TaskResultResponse
        else:
            # Should not happen if status is completed, but handle defensively
            return TaskResultResponse(
                task_id=task_id,
                status="failed",
                progress=progress_str,
                error="Completed status but no result found."
            )
    elif status_str == "failed":
        return TaskResultResponse(
            task_id=task_id,
            status=status_str,
            progress=progress_str,
            error=error_str.decode('utf-8') if error_str else "Unknown error."
        )
    else: # pending, in_progress
        return TaskResultResponse(
            task_id=task_id,
            status=status_str,
            progress=progress_str,
            message="Task is still processing."
        )

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Keyword Clustering API. Use /cluster_keywords to perform clustering."}
