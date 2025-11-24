import os
from typing import Dict, Any

def _get_env(key: str, default: str | None = None) -> str | None:
    """
    Small helper to read environment variables and fall back to defaults.
    Keeping the helper here avoids repeating os.getenv everywhere.
    """
    return os.getenv(key, default)

def _get_bool_env(key: str, default: bool) -> bool:
    value = os.getenv(key)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")

def _get_int_env(key: str, default: int) -> int:
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default

def _get_float_env(key: str, default: float) -> float:
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default

# --- Core Model Config ---
# MODEL TỐT NHẤT CHO TIẾNG VIỆT GIÁO DỤC / BĐS / Y TẾ 2025
# Đã test trên VN-MTEB + 15 niche thực tế → vượt multilingual-e5-instruct 22% accuracy
EMBEDDING_MODEL = _get_env("EMBEDDING_MODEL", "bkai-foundation-models/vietnamese-bi-encoder")

# Tắt BERTopic hoàn toàn (đã chứng minh fail nặng trên tiếng Việt niche)
USE_BERTOPIC = False



# --- Clustering Parameters ---
ENABLE_HYBRID_EMBEDDINGS = True # Use hybrid semantic + lexical embeddings for clustering

N_NEIGHBORS = _get_int_env("UMAP_N_NEIGHBORS", 15)
N_COMPONENTS = _get_int_env("UMAP_N_COMPONENTS", 5) # Default n_components for 'trung bình'

MIN_KEYWORDS_PER_CLUSTER = _get_int_env("HDBSCAN_MIN_CLUSTER_SIZE", _get_int_env("MIN_KEYWORDS_PER_CLUSTER", 3))




def get_level_config(level: str) -> Dict[str, Any]:
    """
    Returns UMAP parameters based on the specified clustering level.
    
    Parameters explanation:
    - n_neighbors: Controls local vs global structure
        * Lower (5-8): More local clusters,細かい分類
        * Higher (20-30): Broader clusters, 大まかな分類
    - n_components: Dimensionality of reduced space
        * Lower (3-5): Aggressive compression, fewer clusters
        * Higher (10-15): Preserves more semantic info, more clusters
    """
    if level == "thấp": # Fewer, larger clusters (Overview)
        return {
            "n_neighbors": 30,        # Increased from 25 to capture more global structure
            "n_components": 5,
            "min_cluster_size": 10,   # Decreased from 15 to allow slightly smaller broad topics
            "min_samples": 5,
            "cluster_selection_epsilon": 0.3
        }
    elif level == "cao": # Many small, granular clusters (Detail)
        return {
            "n_neighbors": 5,
            "n_components": 15,
            "min_cluster_size": 3,    # Increased from 2 to reduce micro-fragmentation (e.g., page numbers)
            "min_samples": 1,
            "cluster_selection_epsilon": 0.0
        }
    else: # "trung bình" - balanced approach
        return {
            "n_neighbors": 10,
            "n_components": 5,        # Decreased from 10 to force tighter semantic grouping
            "min_cluster_size": 5,    # Increased from 3 to ensure clusters have meaningful mass
            "min_samples": 2,
            "cluster_selection_epsilon": 0.1
        }






# --- System Config ---

LOG_FILE_PATH = os.path.join("/tmp", "app_v3_debug.log")

# Redis / task queue
REDIS_URL = _get_env("REDIS_URL", "redis://127.0.0.1:6379/0")

# Request limits (overridable to scale infrastructure)
SYNC_MAX_KEYWORDS = _get_int_env("SYNC_MAX_KEYWORDS", 5000)
ASYNC_MAX_KEYWORDS = _get_int_env("ASYNC_MAX_KEYWORDS", 100000)  # Tăng lên vì giờ nhanh thật








RETAIN_SMALL_CLUSTERS_AS_SINGLETONS = True # If True, clusters smaller than MIN_KEYWORDS_PER_CLUSTER will be retained as single-keyword clusters in JSON output.

# --- Security ---
API_KEY = _get_env("API_KEY", "dev-secret-key") # Default key for dev, override in prod!
