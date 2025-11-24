# keyword_cluster_app/worker.py
import logging
import json
from arq import ArqRedis
from arq.connections import RedisSettings
from typing import Dict, Any

from keyword_cluster_app.services.clustering_service import ClusteringService
from keyword_cluster_app.config import REDIS_URL

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

async def background_process_clustering(ctx: Dict[str, Any], task_id: str, payload: Dict[str, Any]):
    """
    Background task to perform keyword clustering.
    """
    redis: ArqRedis = ctx['redis']
    
    # Update task status to in_progress
    await redis.set(f"task:{task_id}:status", "in_progress")
    await redis.set(f"task:{task_id}:progress", "0%")
    logger.info(f"Task {task_id}: Started processing clustering for {len(payload.get('raw_keywords_with_volume', []))} keywords.")

    try:
        # Call the main clustering logic
        service = ClusteringService()
        results = service.process_clustering(
            raw_keywords_with_volume=payload['raw_keywords_with_volume'],
            level=payload.get('level', 'trung bình'),
            min_cluster_size_override=payload.get('min_cluster_size_override', payload.get('min_cluster_size', None)),
            clustering_method=payload.get('clustering_method', 'semantic'),
        )
        
        # Store results and update status to completed
        await redis.set(f"task:{task_id}:status", "completed")
        await redis.set(f"task:{task_id}:progress", "100%")
        await redis.set(f"task:{task_id}:result", json.dumps(results, ensure_ascii=False))
        logger.info(f"Task {task_id}: Completed successfully.")

    except Exception as e:
        # Store error and update status to failed
        await redis.set(f"task:{task_id}:status", "failed")
        await redis.set(f"task:{task_id}:error", str(e))
        logger.exception(f"Task {task_id}: Failed during clustering.")

class WorkerSettings:
    functions = [background_process_clustering]
    redis_settings = RedisSettings.from_dsn(REDIS_URL)
    max_jobs = 1 # Process one job at a time per worker instance
    keep_result = 3600 # Keep results for 1 hour (in seconds)
    keep_result_forever = False # Do not keep results forever
    job_timeout = 3600 # Max 1 hour for a job to complete
    # You can add more settings here, e.g., on_startup, on_shutdown
