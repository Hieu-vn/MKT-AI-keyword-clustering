# Kế hoạch điều chỉnh Logic SEO dựa trên kiến thức chuyên môn

## 📋 TỔNG QUAN

Dựa trên kiến thức chuyên môn từ Ahrefs, Semrush, Moz, chúng ta cần điều chỉnh các metric sau:

---

## ✅ CÁC METRIC GIỮ NGUYÊN (Đã chính xác)

### 1. Question Detection
- **Logic hiện tại**: Pattern matching với từ khóa tiếng Việt
- **Đánh giá**: ✅ CHÍNH XÁC (dựa trên ngữ pháp chuẩn)
- **Hành động**: Giữ nguyên, bổ sung thêm pattern "Bao nhiêu" (How much)

### 2. Keyword Type Classification
- **Logic hiện tại**: 
  - Short-tail: ≤2 từ
  - Mid-tail: 3-4 từ
  - Long-tail: ≥5 từ
- **Đánh giá**: ⚠️ CẦN ĐIỀU CHỈNH NHỎ
- **Chuẩn ngành**: Long-tail là ≥4 từ (không phải ≥5)
- **Hành động**: Sửa lại:
  - Short-tail: 1-2 từ
  - Mid-tail: 3 từ
  - Long-tail: ≥4 từ

### 3. Related Keywords (TF-IDF)
- **Logic hiện tại**: TF-IDF vectorization
- **Đánh giá**: ✅ CHÍNH XÁC (phương pháp chuẩn NLP)
- **Hành động**: Giữ nguyên

---

## ⚠️ CÁC METRIC CẦN ĐIỀU CHỈNH

### 4. Difficulty Estimation

#### Vấn đề hiện tại
```python
# Logic hiện tại - KHÔNG CHÍNH XÁC
base_kd = 50
if volume > 50000: base_kd += 30  # Giả định
elif volume > 10000: base_kd += 20  # Giả định
if words >= 5: base_kd -= 20  # Giả định
```

#### Logic mới (Dựa trên kiến thức chuyên môn)
```python
def _estimate_difficulty_v2(text: str, volume: int) -> dict:
    """
    Ước lượng KD dựa trên rule of thumb từ WordStream/Semrush.
    Trả về dict với 'score' và 'confidence'.
    """
    words = len(text.split())
    
    # Rule: KD = 20 + (Log(Volume) × 10) cho short-tail
    if volume > 0:
        base_kd = 20 + (math.log10(volume) * 10)
    else:
        base_kd = 10
    
    # Điều chỉnh theo độ dài (Long-tail dễ hơn 50-70%)
    if words >= 4:  # Long-tail
        base_kd = base_kd * 0.4  # Giảm 60%
    elif words == 3:  # Mid-tail
        base_kd = base_kd * 0.7  # Giảm 30%
    # Short-tail (1-2 từ): giữ nguyên
    
    # Giới hạn 0-100
    kd = max(0, min(100, int(base_kd)))
    
    # Xác định confidence level
    if volume < 100:
        confidence = "high"  # Dễ dự đoán (luôn dễ)
    elif volume > 10000:
        confidence = "low"  # Khó dự đoán (cần SERP data)
    else:
        confidence = "medium"
    
    return {
        "score": kd,
        "confidence": confidence,
        "note": "Ước lượng dựa trên volume và độ dài. Không thay thế SERP analysis."
    }
```

**Nguồn**: WordStream Guide, Semrush  
**Độ tin cậy**: Trung bình

---

### 5. Commercial Score

#### Vấn đề hiện tại
```python
# Logic hiện tại - CƠ BẢN NHƯNG CÓ THỂ CẢI THIỆN
if "mua" in text: score += 50
if "review" in text: score += 30
```

#### Logic mới (Dựa trên tier chuyên môn)
```python
def _calculate_commercial_score_v2(text: str, micro_intent: str) -> dict:
    """
    Tính transactional signal dựa trên tier từ Backlinko/Moz.
    """
    text_lower = text.lower()
    score = 0
    tier = "Tier 4"
    
    # Tier 1: Ý định rất cao (80-100)
    tier1_words = ["mua", "order", "đặt hàng", "thanh toán", "coupon", "khuyến mãi"]
    if any(w in text_lower for w in tier1_words):
        score = 85
        tier = "Tier 1"
    
    # Tier 2: Ý định cao (60-80)
    elif any(w in text_lower for w in ["review", "đánh giá", "so sánh", "tốt nhất", "top"]):
        score = 70
        tier = "Tier 2"
    
    # Tier 3: Ý định trung bình (30-50)
    elif any(w in text_lower for w in ["cách dùng", "hướng dẫn", "sử dụng"]):
        score = 40
        tier = "Tier 3"
    
    # Tier 4: Ý định thấp (0-20)
    elif any(w in text_lower for w in ["là gì", "định nghĩa", "khái niệm"]):
        score = 10
        tier = "Tier 4"
    else:
        score = 20  # Default
    
    # Điều chỉnh theo modifiers
    if any(w in text_lower for w in ["rẻ", "giảm giá", "sale"]):
        score = min(100, score + 15)
    if any(w in text_lower for w in ["miễn phí", "free"]):
        score = max(0, score - 15)
    if any(w in text_lower for w in ["ở đâu", "địa chỉ", "gần"]):
        score = min(100, score + 10)
    
    return {
        "score": score,
        "tier": tier,
        "note": "Transactional signal (0-100). Không phải CPC thực tế."
    }
```

**Nguồn**: Backlinko, Moz, Semrush  
**Độ tin cậy**: Cao

---

### 6. SERP Features Prediction

#### Vấn đề hiện tại
```python
# Logic hiện tại - KHÔNG CHÍNH XÁC (dự đoán 100%)
if "cách" in text:
    features.append("Featured Snippet (Steps)")
    features.append("Video Pack")
```

#### Logic mới (Dựa trên tỷ lệ thống kê)
```python
def _predict_serp_features_v2(text: str, micro_intent: str, is_question: bool) -> dict:
    """
    Dự đoán SERP features với xác suất dựa trên Semrush/Ahrefs stats.
    """
    text_lower = text.lower()
    features = []
    probabilities = {}
    
    # Featured Snippet (40-50% cho question keywords)
    if is_question:
        if "là gì" in text_lower or "gì" in text_lower:
            features.append("Featured Snippet (Paragraph)")
            probabilities["Featured Snippet"] = "60-70%"
        elif "cách" in text_lower:
            features.append("Featured Snippet (Steps)")
            probabilities["Featured Snippet"] = "50-60%"
    
    # Video Pack (40-50% cho how-to)
    if any(w in text_lower for w in ["cách", "hướng dẫn", "tutorial"]):
        features.append("Video Pack")
        probabilities["Video Pack"] = "40-50%"
    elif any(w in text_lower for w in ["review", "unboxing"]):
        features.append("Video Pack")
        probabilities["Video Pack"] = "30-40%"
    
    # Shopping Ads (70-80% cho transactional)
    if any(w in text_lower for w in ["mua", "giá"]):
        features.append("Shopping Ads")
        probabilities["Shopping Ads"] = "70-80%"
    
    # Local Pack (85-90% cho location-based)
    if any(w in text_lower for w in ["ở đâu", "gần", "địa chỉ"]):
        features.append("Local Pack (Map)")
        probabilities["Local Pack"] = "85-90%"
    
    # Default
    if not features:
        features.append("Organic Blue Links")
        probabilities["Organic"] = "100%"
    
    return {
        "features": features,
        "probabilities": probabilities,
        "note": "Dự đoán dựa trên pattern. Cần verify bằng Google Search."
    }
```

**Nguồn**: Semrush SERP Features, Ahrefs  
**Độ tin cậy**: Trung bình (biến động theo niche)

---

### 7. Content Format Suggestion

#### Logic hiện tại - CƠ BẢN NHƯNG CÓ THỂ CẢI THIỆN

#### Logic mới (Thêm tỷ lệ chính xác)
```python
def _determine_content_format_v2(cluster_name: str, keywords: List[str]) -> dict:
    """
    Gợi ý content format với độ tin cậy dựa trên Surfer SEO/HubSpot.
    """
    name_lower = cluster_name.lower()
    
    # Listicle (80-90%)
    if any(w in name_lower for w in ["top", "best", "tốt nhất"]):
        return {
            "format": "Listicle / Ranking",
            "confidence": "80-90%",
            "note": "Dùng numbered list, mỗi item là H2"
        }
    
    # How-to Guide (90-95%)
    if any(w in name_lower for w in ["cách", "hướng dẫn", "làm sao"]):
        return {
            "format": "Step-by-Step Guide (How-to)",
            "confidence": "90-95%",
            "note": "Dùng numbered steps, thêm video nếu có thể"
        }
    
    # Review Article (95%)
    if any(w in name_lower for w in ["review", "đánh giá"]):
        return {
            "format": "Review / Comparison Article",
            "confidence": "95%",
            "note": "Pros/cons, ratings, comparison table"
        }
    
    # Comparison (90%)
    if any(w in name_lower for w in ["so sánh", "vs"]):
        return {
            "format": "Comparison Article",
            "confidence": "90%",
            "note": "Side-by-side comparison table"
        }
    
    # Definition (95%)
    if any(w in name_lower for w in ["là gì", "định nghĩa"]):
        return {
            "format": "Wiki / Definition Article",
            "confidence": "95%",
            "note": "Định nghĩa ngắn gọn 40-60 từ ở đầu"
        }
    
    # Default
    return {
        "format": "Standard Blog Post",
        "confidence": "60%",
        "note": "Check SERP để xác định format chính xác"
    }
```

**Nguồn**: Surfer SEO, HubSpot  
**Độ tin cậy**: Cao

---

## 🔄 THAY ĐỔI TRONG DATA MODEL

### Cấu trúc mới cho các metric

```python
# Thay vì trả về giá trị đơn giản:
"difficulty": 70

# Trả về object với metadata:
"difficulty": {
    "score": 70,
    "confidence": "medium",
    "note": "Ước lượng dựa trên volume và độ dài"
}

# Tương tự cho các metric khác:
"commercial_intent": {
    "score": 85,
    "tier": "Tier 1",
    "note": "Transactional signal, không phải CPC"
}

"serp_features": {
    "features": ["Featured Snippet (Steps)", "Video Pack"],
    "probabilities": {
        "Featured Snippet": "50-60%",
        "Video Pack": "40-50%"
    },
    "note": "Dự đoán, cần verify"
}
```

---

## 📝 HÀNH ĐỘNG TIẾP THEO

### Giai đoạn 1: Cập nhật code (Ưu tiên cao)
1. ✅ Sửa Keyword Type: Long-tail từ ≥5 → ≥4 từ
2. ✅ Thêm pattern "Bao nhiêu" vào Question Detection
3. ✅ Cập nhật Difficulty Estimation với công thức mới
4. ✅ Cập nhật Commercial Score với tier system
5. ✅ Cập nhật SERP Features với probabilities
6. ✅ Cập nhật Content Format với confidence

### Giai đoạn 2: Cập nhật tài liệu
1. Cập nhật `API_DOCUMENTATION.md` với cấu trúc mới
2. Thêm disclaimer rõ ràng về độ tin cậy
3. Thêm link tham khảo nguồn

### Giai đoạn 3: Testing
1. Test với dataset toán.csv
2. So sánh kết quả trước/sau
3. Verify logic với case thực tế

---

## ⚠️ LƯU Ý QUAN TRỌNG

1. **Tất cả các metric ước lượng** (không có SERP data) đều cần disclaimer rõ ràng
2. **Luôn khuyến nghị** user check SERP thực tế để verify
3. **Độ tin cậy** phải được hiển thị rõ ràng trong response
4. **Không claim** là chính xác 100% khi không có dữ liệu SERP

---

**Tài liệu tham khảo đầy đủ**: Xem `SEO_METRICS_KNOWLEDGE_BASE.md`
