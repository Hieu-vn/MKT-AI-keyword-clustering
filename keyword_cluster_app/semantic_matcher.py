from typing import List, Tuple, Dict, Any
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity



def rank_keywords_by_semantic_centrality(
    keyword_texts: List[str], keyword_embeddings: np.ndarray
) -> List[Tuple[str, float]]:
    """
    Sắp xếp từ khóa theo độ trung tâm ngữ nghĩa (semantic centrality)
    Input:
        - keyword_texts: danh sách từ khóa (gốc)
        - keyword_embeddings: np.ndarray shape (n_keywords, embedding_dim)
    Output:
        - List (keyword, centrality_score)
    """
    centroid = np.mean(keyword_embeddings, axis=0, keepdims=True)
    similarities = cosine_similarity(keyword_embeddings, centroid).flatten()
    keyword_scores = list(zip(keyword_texts, similarities))
    keyword_scores.sort(key=lambda x: x[1], reverse=True)
    return keyword_scores


def get_top_n_representative_keywords(
    keyword_texts: List[str], keyword_embeddings: np.ndarray, top_n: int = 3
) -> List[str]:
    """
    Trả ra top-N từ khóa tiêu biểu nhất (semantic + lexical)
    """
    ranked = rank_keywords_by_semantic_centrality(keyword_texts, keyword_embeddings)
    top_keywords = [kw for kw, score in ranked[:top_n]]
    return top_keywords




def get_best_cluster_name(
    cluster_keywords: List[Dict[str, Any]],
    cluster_embeddings: np.ndarray | None = None,
    max_length: int = 70,
) -> str:
    """
    Chọn tên cụm bằng cách lấy từ khóa trung tâm ngữ nghĩa nhất.
    """
    if not cluster_keywords:
        return ""

    texts = [kw.get("original_text") or kw.get("text", "") for kw in cluster_keywords]

    if cluster_embeddings is not None and cluster_embeddings.size > 0:
        ranked_keywords = rank_keywords_by_semantic_centrality(texts, cluster_embeddings)
        if ranked_keywords:
            return ranked_keywords[0][0] # Return the most central keyword
    
    # Fallback to the first keyword if embeddings are not available or not effective
    return texts[0] if texts else ""
