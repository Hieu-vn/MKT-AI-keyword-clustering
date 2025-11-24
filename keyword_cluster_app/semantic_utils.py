"""
Module for advanced semantic and lexical analysis functions.

This module will contain functions for:
- Calculating lexical similarity (Jaccard, n-gram overlap).
- Creating hybrid embedding vectors (e.g., semantic + lexical).
- Scoring and re-ranking cluster names.
"""
from typing import List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity




def create_hybrid_embeddings(
    texts: List[str],
    semantic_embeddings: np.ndarray,
    weight_semantic: float = 0.25,
    weight_lexical: float = 0.75
) -> np.ndarray:
    """
    Creates hybrid embeddings by combining semantic (e.g., E5) and lexical (TF-IDF) vectors.

    This approach captures both the deep meaning of keywords and their surface-level
    textual features, addressing the user's feedback on word order and exact matching.

    Args:
        texts: The list of original keywords.
        semantic_embeddings: The pre-computed dense embeddings (e.g., from E5).
        weight_semantic: The weight to apply to the semantic part of the vector.
        weight_lexical: The weight to apply to the lexical part of the vector.

    Returns:
        A numpy array of the final hybrid embeddings, normalized.
    """
    if not texts:
        return np.array([])

    # 1. Create lexical vectors using TF-IDF with character n-grams
    # This captures word order and sub-string patterns effectively.
    tfidf_vectorizer = TfidfVectorizer(
        analyzer='char',
        ngram_range=(2, 4),
        max_features=2048, # Limit feature space to prevent excessive memory usage
        norm='l2' # The vectorizer will L2-normalize the output
    )
    lexical_embeddings = tfidf_vectorizer.fit_transform(texts).toarray()

    # 2. Ensure semantic embeddings are also L2 normalized (should already be, but good practice)
    normalized_semantic = normalize(semantic_embeddings, norm='l2')

    # 3. Apply weights
    weighted_semantic = normalized_semantic * weight_semantic
    weighted_lexical = lexical_embeddings * weight_lexical

    # 4. Concatenate to create the hybrid vector
    hybrid_embeddings = np.hstack([weighted_semantic, weighted_lexical])

    # 5. Final normalization of the combined vector
    final_hybrid_embeddings = normalize(hybrid_embeddings, norm='l2')

    return final_hybrid_embeddings


