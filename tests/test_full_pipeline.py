import numpy as np
import pytest

from keyword_cluster_app import intent_setfit
from keyword_cluster_app.clustering_heavy import (
    calculate_opportunity_fallback,
    find_optimal_min_cluster_size,
    process_clustering,
)
from keyword_cluster_app.semantic_matcher import get_best_cluster_name


def test_detect_intent_hybrid_uses_rules(monkeypatch):
    results = intent_setfit.detect_intent_hybrid(
        ["mua iphone 15", "cách học python hiệu quả"]
    )
    assert results[0] == "giao dịch"
    assert results[1] == "thông tin"


def test_best_cluster_name_prefers_semantic_center():
    keywords = [
        {"original_text": "học python cơ bản", "volume": 1000},
        {"original_text": "học lập trình python", "volume": 1200},
        {"original_text": "python nâng cao", "volume": 200},
    ]
    embeddings = np.array(
        [
            [0.1, 0.2, 0.3],
            [0.15, 0.22, 0.35],
            [0.9, 0.9, 0.95],
        ]
    )
    name = get_best_cluster_name(keywords, embeddings)
    assert "học" in name.lower()


def test_calculate_opportunity_fallback_positive():
    score = calculate_opportunity_fallback("cách học python tại nhà", 800, "thông tin")
    assert score >= 1.0


def test_find_optimal_min_cluster_size_returns_candidate():
    rng = np.random.default_rng(42)
    a = rng.normal(loc=0.0, scale=0.1, size=(10, 4))
    b = rng.normal(loc=5.0, scale=0.1, size=(10, 4))
    embeddings = np.vstack([a, b])
    best = find_optimal_min_cluster_size(embeddings, base_size=3)
    assert best >= 2


def test_process_clustering_with_mocks(monkeypatch):
    sample_keywords = [
        {"text": "học lập trình python", "volume": 1200},
        {"text": "học python cho người mới", "volume": 800},
        {"text": "cách học lập trình python", "volume": 600},
        {"text": "mua iphone 15 pro max", "volume": 5000},
        {"text": "giá iphone 15 pro max", "volume": 4200},
    ]

    def fake_embeddings(texts):
        base = np.arange(len(texts) * 4).reshape(len(texts), 4).astype(float)
        return base / np.linalg.norm(base, axis=1, keepdims=True)

    monkeypatch.setattr(
        "keyword_cluster_app.clustering_heavy.get_embeddings", fake_embeddings
    )
    monkeypatch.setattr(
        "keyword_cluster_app.clustering_heavy.sentence_model", object()
    )
    monkeypatch.setattr(
        "keyword_cluster_app.clustering_heavy.detect_intent",
        lambda keywords: ["thông tin"] * len(keywords),
    )
    monkeypatch.setattr(
        "keyword_cluster_app.clustering_heavy.generate_llm_insights",
        lambda keywords: {"summary": None, "content_ideas": None},
    )
    monkeypatch.setattr(
        "keyword_cluster_app.clustering_heavy.ENABLE_SERP_ENRICHMENT", False, raising=False
    )
    monkeypatch.setattr(
        "keyword_cluster_app.clustering_heavy.ENABLE_LOCAL_LLM", False, raising=False
    )
    monkeypatch.setattr(
        "keyword_cluster_app.clustering_heavy.find_optimal_min_cluster_size",
        lambda embeddings, base: base,
    )

    results = process_clustering(sample_keywords)
    assert results["summary"]["total_keywords_processed"] == len(sample_keywords)
    assert results["summary"]["total_clusters_found"] >= 1
    cluster_values = list(results["clusters"].values())
    assert all(
        cluster["opportunity_score"] >= 1.0 for cluster in cluster_values if "opportunity_score" in cluster
    )
