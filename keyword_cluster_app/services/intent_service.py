import re
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

class IntentService:
    """
    Service to classify search intent of keywords using Hybrid approach (Regex + Semantic).
    
    Hierarchy:
    - TRANSACTIONAL
        - BUY: mua, order, đặt hàng...
        - PRICE: giá, chi phí, bao nhiêu...
        - DISCOUNT: khuyến mãi, voucher, giảm giá...
    - INFORMATIONAL
        - DEFINITION: là gì, khái niệm, ý nghĩa...
        - GUIDE: cách, hướng dẫn, mẹo...
        - KNOWLEDGE: tài liệu, kiến thức, lý thuyết...
    - COMMERCIAL_INVESTIGATION
        - REVIEW: review, đánh giá, có tốt không...
        - COMPARISON: so sánh, vs, khác nhau...
        - BEST_LIST: top, tốt nhất, xếp hạng...
    - NAVIGATIONAL
        - LOCATION: địa chỉ, ở đâu, shop...
        - BRAND: website, trang chủ, login...
        - DOWNLOAD: tải, download, app...
    """

    # Regex Patterns for High Precision
    INTENT_PATTERNS = {
        "TRANSACTIONAL": {
            "BUY": [r"mua", r"bán", r"order", r"đặt hàng", r"thanh lý", r"cần tìm", r"cung cấp"],
            "PRICE": [r"giá", r"chi phí", r"bao nhiêu tiền", r"bảng giá", r"báo giá", r"tốn bao nhiêu"],
            "DISCOUNT": [r"khuyến mãi", r"giảm giá", r"voucher", r"coupon", r"deal", r"ưu đãi"]
        },
        "INFORMATIONAL": {
            "DEFINITION": [r"là gì", r"ý nghĩa", r"khái niệm", r"định nghĩa", r"thế nào là"],
            "GUIDE": [r"cách", r"hướng dẫn", r"mẹo", r"bí quyết", r"làm sao", r"như thế nào", r"các bước"],
            "KNOWLEDGE": [r"tài liệu", r"giáo trình", r"bài tập", r"lý thuyết", r"công thức", r"kiến thức", r"tìm hiểu", r"nguyên lý"]
        },
        "COMMERCIAL_INVESTIGATION": {
            "REVIEW": [r"review", r"đánh giá", r"có tốt không", r"trải nghiệm", r"trên tay", r"uy tín không"],
            "COMPARISON": [r"so sánh", r"khác nhau", r"hay", r"vs", r"phân biệt"],
            "BEST_LIST": [r"top", r"tốt nhất", r"xếp hạng", r"đáng mua", r"bán chạy", r"hot nhất"]
        },
        "NAVIGATIONAL": {
            "LOCATION": [r"địa chỉ", r"ở đâu", r"tại đâu", r"shop", r"cửa hàng", r"trung tâm", r"chi nhánh"],
            "BRAND": [r"website", r"trang chủ", r"đăng nhập", r"login", r"facebook", r"fanpage", r"chính hãng"],
            "DOWNLOAD": [r"tải", r"download", r"app", r"ứng dụng", r"cài đặt", r"apk", r"ios", r"android"]
        }
    }

    # Prototypes for Semantic Matching (Fallback)
    # Representative keywords for each sub-intent
    INTENT_PROTOTYPES = {
        ("TRANSACTIONAL", "BUY"): "mua hàng đặt hàng online",
        ("TRANSACTIONAL", "PRICE"): "giá bao nhiêu tiền bảng giá",
        ("TRANSACTIONAL", "DISCOUNT"): "khuyến mãi giảm giá voucher",
        ("INFORMATIONAL", "DEFINITION"): "là gì định nghĩa khái niệm",
        ("INFORMATIONAL", "GUIDE"): "hướng dẫn cách làm mẹo",
        ("INFORMATIONAL", "KNOWLEDGE"): "tài liệu kiến thức bài tập",
        ("COMMERCIAL_INVESTIGATION", "REVIEW"): "review đánh giá nhận xét",
        ("COMMERCIAL_INVESTIGATION", "COMPARISON"): "so sánh phân biệt khác nhau",
        ("COMMERCIAL_INVESTIGATION", "BEST_LIST"): "top tốt nhất xếp hạng",
        ("NAVIGATIONAL", "LOCATION"): "địa chỉ cửa hàng ở đâu",
        ("NAVIGATIONAL", "BRAND"): "trang chủ website chính hãng",
        ("NAVIGATIONAL", "DOWNLOAD"): "tải download ứng dụng"
    }

    def __init__(self):
        self.prototype_embeddings = None
        self.prototype_keys = [] # List of (Main, Sub) tuples corresponding to embeddings

    def _ensure_prototypes_loaded(self, model):
        """Lazy load prototype embeddings using the provided model."""
        if self.prototype_embeddings is None and model is not None:
            logger.info("Calculating intent prototype embeddings...")
            texts = list(self.INTENT_PROTOTYPES.values())
            self.prototype_keys = list(self.INTENT_PROTOTYPES.keys())
            self.prototype_embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)

    def classify(self, keyword: str, embedding: Optional[np.ndarray] = None, model = None) -> Dict[str, str]:
        """
        Classifies a single keyword.
        Returns dict with 'intent' and 'sub_intent'.
        """
        keyword_lower = keyword.lower()
        
        # 1. Regex Classification (Priority)
        for main_intent, sub_intents in self.INTENT_PATTERNS.items():
            for sub_intent, patterns in sub_intents.items():
                for pattern in patterns:
                    if re.search(pattern, keyword_lower):
                        return {"intent": main_intent, "sub_intent": sub_intent}
        
        # 2. Semantic Classification (Fallback)
        if embedding is not None and model is not None:
            self._ensure_prototypes_loaded(model)
            if self.prototype_embeddings is not None:
                # Calculate similarity
                sims = cosine_similarity([embedding], self.prototype_embeddings).flatten()
                best_idx = np.argmax(sims)
                best_score = sims[best_idx]
                
                # Threshold for semantic match (adjust as needed)
                if best_score > 0.4: 
                    main, sub = self.prototype_keys[best_idx]
                    return {"intent": main, "sub_intent": sub}

        return {"intent": "UNCATEGORIZED", "sub_intent": "NONE"}

    def classify_batch(self, keywords: List[str], embeddings: Optional[np.ndarray] = None, model = None) -> List[Dict[str, str]]:
        """
        Classifies a batch of keywords.
        """
        results = []
        for i, kw in enumerate(keywords):
            emb = embeddings[i] if embeddings is not None else None
            results.append(self.classify(kw, emb, model))
        return results
