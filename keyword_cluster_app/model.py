
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Optional, Dict

from keyword_cluster_app.config import EMBEDDING_MODEL

model: Optional[SentenceTransformer] = None
_embedding_cache: Dict[str, np.ndarray] = {} # In-memory cache for embeddings

def _detect_device() -> str:
    """
    Chọn device cho model: ưu tiên GPU nếu có.
    """
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
    except Exception:
        pass
    return "cpu"

def load_model() -> None:
    """
    Load SentenceTransformer model vào biến global 'model'.
    """
    global model
    device = _detect_device()
    try:
        print(f"Loading {EMBEDDING_MODEL} on {device}...")
        model = SentenceTransformer(EMBEDDING_MODEL, device=device)
        print("Model loaded.")
    except Exception as e:
        print(f"Error loading SentenceTransformer model '{EMBEDDING_MODEL}': {e}")
        print("Clustering functionality will not work. Please check your internet connection and model name.")
        model = None

# Tự động load khi import module
load_model()

def get_embeddings(
    keywords: List[str],
    batch_size: int = 512,
    show_progress_bar: bool = False,
    normalize_embeddings: bool = True,
    convert_to_numpy: bool = True
) -> Optional[np.ndarray]:
    """
    Generates embeddings for a list of keywords using the pre-loaded model,
    utilizing an in-memory cache to speed up processing.
    """
    if model is None:
        return None
    
    prefixed_keywords_map = {}
    for kw in keywords:
        # Prefix cho instruct models (e5-instruct cần "query: ")
        prefixed_keywords_map[kw] = f"query: {kw}" if "instruct" in EMBEDDING_MODEL else kw

    # Separate keywords into those in cache and those needing encoding
    cached_embeddings = []
    to_encode_texts = []
    original_order_map = {} # To reconstruct the original order

    for i, kw in enumerate(keywords):
        prefixed_kw = prefixed_keywords_map[kw]
        if prefixed_kw in _embedding_cache:
            cached_embeddings.append((i, _embedding_cache[prefixed_kw]))
        else:
            to_encode_texts.append((i, prefixed_kw))
        original_order_map[i] = None # Placeholder for final embeddings

    if to_encode_texts:
        # Extract only the texts to encode, preserving their original index
        texts_to_encode_only = [item[1] for item in to_encode_texts]
        new_embeddings = model.encode(
            texts_to_encode_only,
            batch_size=batch_size,
            show_progress_bar=show_progress_bar,
            normalize_embeddings=normalize_embeddings,
            convert_to_tensor=not convert_to_numpy,
        )
        if not convert_to_numpy:
            new_embeddings = new_embeddings.cpu().numpy()
        
        # Store new embeddings in cache and map to original order
        for i, (original_idx, prefixed_kw) in enumerate(to_encode_texts):
            _embedding_cache[prefixed_kw] = new_embeddings[i]
            original_order_map[original_idx] = new_embeddings[i]

    # Add cached embeddings to the original order map
    for original_idx, embedding in cached_embeddings:
        original_order_map[original_idx] = embedding
    
    # Reconstruct embeddings in the original order
    final_embeddings = [original_order_map[i] for i in range(len(keywords))]

    return np.array(final_embeddings)