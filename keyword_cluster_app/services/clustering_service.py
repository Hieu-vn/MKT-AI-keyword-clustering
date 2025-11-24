import logging
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter
from sklearn.metrics.pairwise import cosine_similarity
from umap import UMAP
from hdbscan import HDBSCAN

from keyword_cluster_app.config import (
    EMBEDDING_MODEL,
    ENABLE_HYBRID_EMBEDDINGS,
    get_level_config,
    RETAIN_SMALL_CLUSTERS_AS_SINGLETONS
)
from keyword_cluster_app.services.intent_service import IntentService
from keyword_cluster_app.model import load_model, model as shared_model
from keyword_cluster_app.utils.text_processing import clean_keyword

logger = logging.getLogger(__name__)

class ClusteringService:
    def __init__(self):
        self.model = self._get_model()
        self.intent_service = IntentService()
        logger.info("ClusteringService initialized.")

    def _get_model(self):
        if shared_model is None:
            logger.info(f"Model not loaded, loading {EMBEDDING_MODEL}...")
            load_model()
            if shared_model is None:
                 raise RuntimeError("Failed to load shared model")
        return shared_model

    def process_clustering(
        self,
        raw_keywords_with_volume: List[Dict[str, Any]],
        level: str = "trung bình",
        min_cluster_size_override: int = None,
        clustering_method: str = "semantic",
    ) -> Dict[str, Any]:
        
        if not raw_keywords_with_volume:
            return {"clusters": {}, "unclustered": [], "summary": {}, "csv_data": ""}

        # 1. Prepare Data
        df = pd.DataFrame(raw_keywords_with_volume)
        df['text'] = df['text'].astype(str)
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce').fillna(0).astype(int)
        df['cleaned'] = df['text'].apply(clean_keyword)

        texts = df['cleaned'].tolist()
        original_texts = df['text'].tolist()
        volumes = df['volume'].tolist()
        total_raw_volume = sum(volumes)

        # 2. Embeddings
        embeddings = self.model.encode(texts, batch_size=512, show_progress_bar=False, normalize_embeddings=True)

        # 3. Intent Classification (Hybrid)
        # Pass embeddings and model to intent service for semantic fallback
        intent_results = self.intent_service.classify_batch(texts, embeddings, self.model)
        df['intent'] = intent_results
        
        intents = df['intent'].tolist()

        # 3. Dimensionality Reduction (UMAP)
        level_config = get_level_config(level)
        # Dynamic parameter adjustment for small datasets to prevent UMAP errors
        n_keywords = len(embeddings)
        umap_params = {
            'n_neighbors': level_config["n_neighbors"],
            'n_components': level_config["n_components"]
        }

        # Dynamic parameter adjustment - ensure UMAP can run safely
        # Rule: n_components must be < n_keywords, and n_neighbors must be <= n_keywords
        # For safety, we use n_components <= n_keywords - 2
        
        # Always adjust if n_components is too large
        if umap_params['n_components'] >= n_keywords - 1:
            umap_params['n_components'] = max(2, min(n_keywords - 2, 5))
            logger.info(f"Adjusted n_components to {umap_params['n_components']} (n_keywords={n_keywords})")
        
        # Always adjust if n_neighbors is too large
        if umap_params['n_neighbors'] >= n_keywords:
            umap_params['n_neighbors'] = max(2, n_keywords - 1)
            logger.info(f"Adjusted n_neighbors to {umap_params['n_neighbors']} (n_keywords={n_keywords})")


        logger.info(f"Clustering with level '{level}': UMAP(n_neighbors={umap_params['n_neighbors']}, n_components={umap_params['n_components']}), HDBSCAN(min_cluster_size={level_config['min_cluster_size']})")

        # For very small datasets, skip UMAP to avoid errors
        if n_keywords < 10:
            logger.warning(f"Very small dataset ({n_keywords} keywords). Skipping UMAP, clustering directly on embeddings.")
            reduced_embeddings = embeddings  # Use original embeddings
        else:
            # --- HYBRID CLUSTERING (Semantic + Lexical) ---
            # Combine Dense Embeddings (AI) with Sparse Matrix (TF-IDF)
            # This improves accuracy by distinguishing similar topics with different specific keywords (e.g., iPhone 14 vs 15)
            
            from sklearn.feature_extraction.text import TfidfVectorizer
            from scipy.sparse import hstack
            
            # 1. Create Lexical Vectors (TF-IDF)
            vectorizer = TfidfVectorizer(min_df=1, analyzer='word', ngram_range=(1, 2))
            tfidf_matrix = vectorizer.fit_transform(original_texts)
            
            # 2. Combine with Semantic Embeddings
            # We weight semantic embeddings higher (e.g., 0.7) but give lexical some weight (0.3)
            # Note: UMAP can handle sparse inputs directly or we can concatenate
            
            # Simple concatenation strategy (proven effective for short text)
            # Normalize embeddings first to ensure fair contribution
            from sklearn.preprocessing import normalize
            normalized_embeddings = normalize(embeddings)
            
            # Convert dense embeddings to sparse format for efficient stacking
            from scipy.sparse import csr_matrix
            sparse_embeddings = csr_matrix(normalized_embeddings)
            
            # Stack them: [Semantic Vectors | Lexical Vectors]
            hybrid_matrix = hstack([sparse_embeddings, tfidf_matrix])
            
            # 3. UMAP Reduction on Hybrid Data
            umap_model = UMAP(
                n_neighbors=umap_params["n_neighbors"],
                n_components=umap_params["n_components"],
                min_dist=0.0,
                metric='cosine', # Cosine works well for high-dim sparse data
                random_state=42,
                n_jobs=1
            )
            reduced_embeddings = umap_model.fit_transform(hybrid_matrix)

        # 4. Clustering (HDBSCAN)
        # Use level_config for HDBSCAN parameters, but allow override
        min_cluster_size = min_cluster_size_override if min_cluster_size_override is not None else level_config["min_cluster_size"]
        min_samples = level_config.get("min_samples", 2)
        cluster_selection_epsilon = level_config.get("cluster_selection_epsilon", 0.0)
        
        clusterer = HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=min_samples,
            cluster_selection_epsilon=cluster_selection_epsilon,
            metric='euclidean',
            cluster_selection_method='eom',
            prediction_data=True
        )
        labels = clusterer.fit_predict(reduced_embeddings)

        # 5. Force-assign noise to nearest cluster (with confidence threshold)
        noise_mask = labels == -1
        num_noise = np.sum(noise_mask)
        
        # Confidence threshold: Only assign if similarity >= this value
        CONFIDENCE_THRESHOLD = 0.65
        
        if num_noise > 0:
            logger.info(f"Found {num_noise} noise keywords. Force-assigning with confidence threshold {CONFIDENCE_THRESHOLD}...")
            
            # Calculate cluster centroids
            unique_labels = set(labels) - {-1}
            centroids = {}
            for label in unique_labels:
                cluster_mask = labels == label
                cluster_embeddings = embeddings[cluster_mask]
                centroids[label] = np.mean(cluster_embeddings, axis=0, keepdims=True)
            
            # Assign each noise point to nearest cluster (if confident enough)
            noise_indices = np.where(noise_mask)[0]
            low_confidence_count = 0
            
            for idx in noise_indices:
                noise_embedding = embeddings[idx:idx+1]  # Keep 2D shape
                
                # Calculate similarity to all centroids
                best_label = None
                best_similarity = -1
                
                for label, centroid in centroids.items():
                    similarity = cosine_similarity(noise_embedding, centroid)[0, 0]
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_label = label
                
                # Only assign if confidence is high enough
                if best_label is not None and best_similarity >= CONFIDENCE_THRESHOLD:
                    labels[idx] = best_label
                else:
                    # Keep as noise but will be grouped into "Low Confidence" cluster later
                    low_confidence_count += 1
            
            logger.info(f"Assigned {num_noise - low_confidence_count} noise keywords to clusters. {low_confidence_count} keywords remain as low-confidence.")

        # 6. Post-processing & Naming
        return self._build_results(original_texts, volumes, labels, embeddings, total_raw_volume, intents)

    def _build_results(self, original_texts, volumes, labels, embeddings, total_raw_volume, intents):
        # Group by label
        cluster_texts = defaultdict(list)
        cluster_volumes = defaultdict(list)
        unclustered_raw = []
        for text, vol, label, intent in zip(original_texts, volumes, labels, intents):
            if label == -1:
                unclustered_raw.append({"text": text, "volume": vol, "intent": intent})
            else:
                cluster_texts[label].append(text)
                cluster_volumes[label].append(vol)
        
        # Generate Names based on highest volume keyword
        cluster_names = {}
        for label, docs in cluster_texts.items():
            vols = cluster_volumes[label]
            if not docs:
                cluster_names[label] = "Unknown Topic"
                continue
            # Find index of max volume
            max_idx = max(range(len(vols)), key=lambda i: vols[i])
            cluster_names[label] = docs[max_idx]
        
        # Build Output Structure
        clusters = {}
        csv_rows = ["Topic,Keyword,Volume,Total Volume Topic,Similarity,Cluster Type,Intent,Sub-Intent"]
        total_processed_keywords = len(original_texts)
        
        # Sort clusters by volume
        cluster_info = []
        for label in set(labels):
            if label == -1: continue
            indices = [i for i, l in enumerate(labels) if l == label]
            total_vol = sum(volumes[i] for i in indices)
            cluster_info.append((label, total_vol, indices))
        
        cluster_info.sort(key=lambda x: x[1], reverse=True)

        for rank, (label, total_vol, indices) in enumerate(cluster_info, 1):
            name = cluster_names.get(label, f"Cụm {rank}")
            
            # Calculate similarity with cluster name (highest volume keyword)
            # Find the index of the keyword that IS the cluster name
            max_vol_in_cluster = max(volumes[i] for i in indices)
            name_keyword_idx = None
            for i in indices:
                if volumes[i] == max_vol_in_cluster and original_texts[i] == name:
                    name_keyword_idx = i
                    break
            
            # If we found the name keyword, calculate similarity against it
            if name_keyword_idx is not None:
                name_embedding = embeddings[name_keyword_idx:name_keyword_idx+1]  # Keep 2D
                cluster_embeddings = embeddings[indices]
                sims = cosine_similarity(cluster_embeddings, name_embedding).flatten()
            else:
                # Fallback: if we can't find the exact name keyword, use centroid
                if len(indices) > 1:
                    cluster_embeddings = embeddings[indices]
                    centroid = np.mean(cluster_embeddings, axis=0, keepdims=True)
                    sims = cosine_similarity(cluster_embeddings, centroid).flatten()
                else:
                    sims = [1.0]

            # Calculate dominant intent (based on Main Intent)
            cluster_intents_list = [intents[i]['intent'] for i in indices]
            dominant_intent = Counter(cluster_intents_list).most_common(1)[0][0] if cluster_intents_list else "UNCATEGORIZED"

            kw_list = []
            for i, sim in zip(indices, sims):
                intent_data = intents[i]
                kw_data = {
                    "text": original_texts[i],
                    "volume": volumes[i],
                    "matching_point": round(float(sim) * 100, 1)  # Convert to 0-100 scale
                }
                kw_list.append(kw_data)
            # --- CORE CLUSTERING DATA ONLY ---
            # No advanced SEO analysis to maximize speed
            
            clusters[name] = {
                "cluster_name": name,
                "keywords": kw_list,
                "total_volume_topic": total_vol
                # "cluster_intent": dominant_intent, # Removed
                # "content_format": content_format, # Removed
                # "parent_topic": None,
                # "related_keywords": related_kws, # Removed
                # "avg_commercial_score": avg_commercial # Removed
            }

        # --- 4. Handle Unclustered Keywords (Noise) ---
        unclustered = []
        total_noise_volume = 0
        total_noise_keywords = 0

        if -1 in labels:
            noise_indices = [i for i, label in enumerate(labels) if label == -1]
            total_noise_keywords = len(noise_indices)
            
            for i in noise_indices:
                keyword_text = original_texts[i]
                vol = volumes[i]
                total_noise_volume += vol
                
                # Create a singleton cluster for noise if configured
                # Or just add to unclustered list
                # For consistency with "clean" output, we might want to group them or list them
                
                # Current logic: Treat as singleton clusters (Topic = Keyword)
                # This ensures EVERY keyword appears in the Excel/JSON list
                
                cluster_name = keyword_text
                kw_data = {
                    "text": keyword_text,
                    "volume": vol,
                    "matching_point": 100.0 # Self-match
                }
                
                clusters[cluster_name] = {
                    "cluster_name": cluster_name,
                    "keywords": [kw_data],
                    "total_volume_topic": vol
                }


        # --- 5. Refine Clusters with Cross-Encoder (The "Accuracy Booster") ---
        # This step verifies each keyword against the cluster center using a Cross-Encoder model.
        # Cross-Encoders are much more accurate than Bi-Encoders (Vectors) for pair comparison.
        
        logger.info("Refining clusters with Cross-Encoder for maximum accuracy...")
        clusters, refined_unclustered = self._refine_clusters_with_cross_encoder(clusters)
        
        # Add refined unclustered keywords back to the main unclustered list
        # Note: In current logic, we might want to treat them as singletons or noise.
        # Let's add them to noise processing logic if needed, or just return as unclustered.
        
        # For now, let's create singleton clusters for these rejected keywords to ensure coverage
        for kw_text in refined_unclustered:
             # Find original volume
             try:
                 idx = original_texts.index(kw_text)
                 vol = volumes[idx]
             except ValueError:
                 vol = 0 # Should not happen
                 
             cluster_name = kw_text
             kw_data = {
                 "text": kw_text,
                 "volume": vol,
                 "matching_point": 100.0
             }
             clusters[cluster_name] = {
                 "cluster_name": cluster_name,
                 "keywords": [kw_data],
                 "total_volume_topic": vol
             }
             total_noise_keywords += 1
             total_noise_volume += vol

        # Summary update
        top10_vol = sum(c['total_volume_topic'] for c in sorted(clusters.values(), key=lambda x: x['total_volume_topic'], reverse=True)[:10])
        top10_percent = round(top10_vol / total_raw_volume * 100, 1) if total_raw_volume > 0 else 0
        
        summary = {
            "total_keywords_processed": len(original_texts),
            "total_clusters_found": len(clusters),
            "top10_cluster_volume_percent": top10_percent,
            "noise_keywords_found": total_noise_keywords,
            "noise_volume": total_noise_volume
        }

        return {
            "clusters": clusters,
            "unclustered_keywords": unclustered, # Original unclustered list
            "summary": summary
        }

    def _refine_clusters_with_cross_encoder(self, clusters: Dict[str, Any], threshold: float = 0.4) -> Tuple[Dict[str, Any], List[str]]:
        """
        Uses a Cross-Encoder to verify if keywords truly belong to their assigned cluster.
        Returns refined clusters and a list of rejected keywords.
        """
        from sentence_transformers import CrossEncoder
        import torch
        
        # Load model (lazy loading to save memory if not used often)
        # Using a lightweight but effective model
        model_name = 'cross-encoder/ms-marco-MiniLM-L-6-v2'
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        try:
            model = CrossEncoder(model_name, device=device)
        except Exception as e:
            logger.error(f"Failed to load Cross-Encoder: {e}. Skipping refinement.")
            return clusters, []

        rejected_keywords = []
        refined_clusters = {}

        for name, data in clusters.items():
            keywords = data['keywords']
            if not keywords:
                continue
                
            # Prepare pairs: (Cluster Name, Keyword Text)
            # Cluster Name acts as the "Anchor" or "Query"
            pairs = [[name, kw['text']] for kw in keywords]
            
            # Predict similarity scores
            scores = model.predict(pairs)
            
            valid_keywords = []
            
            for i, score in enumerate(scores):
                # Sigmoid conversion if model outputs logits (ms-marco models usually output logits)
                # But CrossEncoder.predict usually returns raw scores. 
                # For ms-marco-MiniLM-L-6-v2, scores are not bounded 0-1.
                # We need to normalize or use a relative threshold.
                # Actually, for this specific model, higher is better. 
                # A safe heuristic threshold for relevance is often around 0 or -2 depending on the model.
                # Let's use a safer approach: If it's the cluster name itself, keep it.
                
                kw = keywords[i]
                
                # Always keep the cluster name keyword itself
                if kw['text'] == name:
                    valid_keywords.append(kw)
                    continue
                
                # For MS MARCO models, scores can range from -10 to 10.
                # A score > 0 usually indicates relevance.
                # Let's be slightly lenient to avoid over-filtering.
                if score > -2.0: 
                    # Update matching point with the high-quality Cross-Encoder score
                    # Normalize score roughly to 0-100 for display
                    # Map -2 to 10 (low), 10 to 100 (high)
                    normalized_score = max(10, min(100, (score + 4) * 10))
                    kw['matching_point'] = round(normalized_score, 1)
                    valid_keywords.append(kw)
                else:
                    rejected_keywords.append(kw['text'])
            
            if valid_keywords:
                data['keywords'] = valid_keywords
                # Recalculate volume
                data['total_volume_topic'] = sum(k['volume'] for k in valid_keywords)
                refined_clusters[name] = data
            else:
                # If all keywords rejected (rare, but possible if cluster name was bad), 
                # the cluster name itself should have been kept.
                pass

        return refined_clusters, rejected_keywords

    def _analyze_micro_intent(self, text: str) -> str:
        """Analyze specific user intent based on keyword patterns."""
        text = text.lower()
        if any(w in text for w in ["mua", "bán", "giá", "chi phí", "khuyến mãi", "thanh lý"]):
            if any(w in text for w in ["ở đâu", "chỗ nào", "địa chỉ"]):
                return "Local Transactional" # Mua ở đâu
            return "Transactional / Pricing"
        if any(w in text for w in ["review", "đánh giá", "có tốt không", "so sánh", "top", "loại nào tốt"]):
            return "Commercial Investigation"
        if any(w in text for w in ["cách", "hướng dẫn", "làm sao", "như thế nào", "bị lỗi", "sửa"]):
            return "Troubleshooting / How-to"
        if any(w in text for w in ["là gì", "định nghĩa", "khái niệm", "ý nghĩa"]):
            return "Definition / Concept"
        if any(w in text for w in ["tải", "download", "link", "phần mềm", "app"]):
            return "Software / Download"
        if any(w in text for w in ["hình ảnh", "mẫu", "video", "clip"]):
            return "Visual / Media"
        return "General Information"

    def _determine_content_format(self, cluster_name: str, keywords: List[str]) -> str:
        """Suggest the best content format for the cluster."""
        # Check cluster name first
        name_intent = self._analyze_micro_intent(cluster_name)
        
        if name_intent == "Commercial Investigation":
            if "top" in cluster_name.lower():
                return "Listicle / Ranking"
            return "Review / Comparison Article"
        
        if name_intent == "Troubleshooting / How-to":
            return "Step-by-Step Guide (How-to)"
            
        if name_intent == "Transactional / Pricing":
            return "Product Page / Category Page"
            
        if name_intent == "Definition / Concept":
            return "Wiki / Definition Article"
            
        if name_intent == "Visual / Media":
            return "Image Gallery / Video Page"

        # Fallback: Check majority of keywords
        if any("tại sao" in k for k in keywords):
            return "Explainer Article"
            
        return "Standard Blog Post"

    def _estimate_difficulty(self, text: str, volume: int) -> int:
        """Estimate Keyword Difficulty (KD) based on heuristics."""
        # Heuristic: Short keywords with high volume are harder.
        # Long-tail keywords are easier.
        words = len(text.split())
        
        base_kd = 50
        
        # Volume factor
        if volume > 50000: base_kd += 30
        elif volume > 10000: base_kd += 20
        elif volume > 1000: base_kd += 10
        elif volume < 100: base_kd -= 10
        
        # Length factor (Longer = Easier)
        if words >= 5: base_kd -= 20
        elif words == 4: base_kd -= 10
        elif words <= 2: base_kd += 15
        
        return max(0, min(100, base_kd))

    def _predict_serp_features(self, text: str, micro_intent: str) -> List[str]:
        """Predict likely SERP features."""
        features = []
        text = text.lower()
        
        if micro_intent == "Troubleshooting / How-to" or "cách" in text:
            features.append("Featured Snippet (Steps)")
            features.append("Video Pack")
            
        if micro_intent == "Definition / Concept" or "là gì" in text:
            features.append("Featured Snippet (Paragraph)")
            
        if micro_intent == "Local Transactional":
            features.append("Local Pack (Map)")
            
        if "top" in text or "review" in text:
            features.append("Star Ratings")
            
        if any(w in text for w in ["giá", "mua"]):
            features.append("Shopping Ads")
            
        if not features:
            features.append("Organic Blue Links")
            
        return features

    def _detect_question(self, text: str) -> tuple[bool, str]:
        """Detect if keyword is a question and classify question type."""
        text_lower = text.lower()
        
        # Vietnamese question patterns
        question_patterns = {
            "what": ["là gì", "là j", "nghĩa là gì", "định nghĩa", "khái niệm"],
            "how": ["cách", "làm sao", "như thế nào", "thế nào", "làm thế nào", "hướng dẫn"],
            "why": ["tại sao", "vì sao", "lý do", "nguyên nhân"],
            "where": ["ở đâu", "chỗ nào", "nơi nào", "địa chỉ"],
            "when": ["khi nào", "bao giờ", "lúc nào"],
            "which": ["loại nào", "cái nào", "nên chọn"],
            "who": ["ai", "người nào"]
        }
        
        for q_type, patterns in question_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                return True, q_type
        
        return False, None

    def _classify_keyword_type(self, text: str) -> str:
        """Classify keyword as short-tail, mid-tail, or long-tail."""
        word_count = len(text.split())
        
        if word_count <= 2:
            return "short-tail"
        elif word_count <= 4:
            return "mid-tail"
        else:
            return "long-tail"

    def _calculate_commercial_score(self, text: str, micro_intent: str) -> int:
        """Calculate commercial intent score (0-100)."""
        text_lower = text.lower()
        score = 0
        
        # High commercial signals (40-50 points)
        high_commercial = ["mua", "bán", "giá", "khuyến mãi", "giảm giá", "thanh lý", "order", "đặt hàng"]
        for word in high_commercial:
            if word in text_lower:
                score += 50
                break
        
        # Medium commercial signals (20-30 points)
        medium_commercial = ["review", "đánh giá", "so sánh", "tốt nhất", "top", "loại nào tốt", "có nên"]
        for word in medium_commercial:
            if word in text_lower:
                score += 30
                break
        
        # Low commercial signals (10-20 points)
        low_commercial = ["cửa hàng", "shop", "store", "chính hãng", "uy tín"]
        for word in low_commercial:
            if word in text_lower:
                score += 15
                break
        
        # Boost based on micro_intent
        if micro_intent == "Transactional / Pricing":
            score = min(100, score + 30)
        elif micro_intent == "Commercial Investigation":
            score = min(100, score + 20)
        elif micro_intent == "Local Transactional":
            score = min(100, score + 25)
        
        return min(100, score)

    def _extract_related_keywords(self, cluster_keywords: List[str], top_n: int = 5) -> List[str]:
        """Extract related keywords using TF-IDF from cluster keywords."""
        if len(cluster_keywords) < 2:
            return []
        
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            
            # Use word-level TF-IDF
            vectorizer = TfidfVectorizer(
                max_features=20,
                ngram_range=(1, 2),
                min_df=1,
                stop_words=None  # Keep all words for Vietnamese
            )
            
            tfidf_matrix = vectorizer.fit_transform(cluster_keywords)
            feature_names = vectorizer.get_feature_names_out()
            
            # Get average TF-IDF scores
            avg_scores = tfidf_matrix.mean(axis=0).A1
            top_indices = avg_scores.argsort()[-top_n:][::-1]
            
            related = [feature_names[i] for i in top_indices]
            
            # Filter out single characters and very short words
            related = [w for w in related if len(w) > 2]
            
            return related[:top_n]
        except Exception as e:
            logger.warning(f"Failed to extract related keywords: {e}")
            return []
