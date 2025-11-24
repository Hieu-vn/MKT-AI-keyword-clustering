# Test API với Postman - Tính năng nâng cao

## 1. Thông tin kết nối
- **URL**: `http://172.16.120.23:8001/cluster_keywords_sync`
- **Method**: `POST`
- **Headers**:
  - `Content-Type`: `application/json`
  - `X-API-Key`: `sk-2631259f7b709b4d7fa370cf86aac259`

## 2. Request Body (Copy vào Postman)

Paste đoạn JSON này vào tab **Body** → **raw** → **JSON**:

```json
{
  "keywords": [
    {"text": "mua iphone 15 pro max", "volume": 50000},
    {"text": "giá iphone 15 pro max", "volume": 40000},
    {"text": "iphone 15 pro max giá rẻ", "volume": 10000},
    {"text": "mua iphone 15 ở đâu", "volume": 8000},
    {"text": "review iphone 15 pro max", "volume": 5000},
    {"text": "đánh giá iphone 15 pro max", "volume": 4000},
    {"text": "có nên mua iphone 15", "volume": 3000},
    {"text": "so sánh iphone 15 và 14", "volume": 2500},
    {"text": "cách chụp màn hình iphone 15", "volume": 2000},
    {"text": "hướng dẫn sử dụng iphone 15", "volume": 1500},
    {"text": "cách cài đặt iphone 15", "volume": 1200},
    {"text": "iphone 15 bị nóng máy", "volume": 1000},
    {"text": "cách sửa lỗi iphone 15", "volume": 800},
    {"text": "iphone 15 là gì", "volume": 500},
    {"text": "tại sao nên mua iphone 15", "volume": 400},
    {"text": "iphone 15 có gì mới", "volume": 300},
    {"text": "top 10 ốp lưng iphone 15", "volume": 2000},
    {"text": "ốp lưng iphone 15 tốt nhất", "volume": 1500},
    {"text": "mua ốp lưng iphone 15", "volume": 1000},
    {"text": "hình ảnh iphone 15", "volume": 5000},
    {"text": "video mở hộp iphone 15", "volume": 3000},
    {"text": "clip review iphone 15", "volume": 2000}
  ],
  "level": "cao",
  "clustering_method": "semantic"
}
```

## 3. Kết quả mong đợi

Sau khi nhấn **Send**, anh sẽ thấy response JSON với các trường mới:

### A. Ở cấp độ Keyword (trong `keywords[]`):
```json
{
  "text": "mua iphone 15 pro max",
  "volume": 50000,
  "matching_point": 100.0,
  "micro_intent": "Transactional / Pricing",
  "difficulty": 70,
  "serp_features": ["Shopping Ads"],
  "is_question": false,
  "question_type": null,
  "keyword_type": "long-tail",
  "commercial_score": 80
}
```

**Giải thích các trường mới:**
- `is_question`: `true` nếu là câu hỏi (ví dụ: "là gì", "cách nào")
- `question_type`: Loại câu hỏi (`what`, `how`, `why`, `where`, `when`)
- `keyword_type`: Độ dài từ khóa (`short-tail`, `mid-tail`, `long-tail`)
- `commercial_score`: Điểm ý định thương mại (0-100, càng cao càng dễ chuyển đổi)

### B. Ở cấp độ Cluster (trong `clusters{}`):
```json
{
  "cluster_name": "mua iphone 15 pro max",
  "keywords": [...],
  "total_volume_topic": 108000,
  "cluster_intent": "TRANSACTIONAL",
  "content_format": "Product Page / Category Page",
  "parent_topic": null,
  "related_keywords": ["iphone", "pro max", "15", "mua", "giá"],
  "avg_commercial_score": 76.7
}
```

**Giải thích các trường mới:**
- `content_format`: Gợi ý định dạng bài viết phù hợp nhất
- `related_keywords`: Các từ khóa liên quan (LSI) nên đề cập trong bài
- `avg_commercial_score`: Điểm thương mại trung bình của cả cluster

## 4. Các ví dụ kết quả thực tế

### Ví dụ 1: Từ khóa câu hỏi
**Input**: `"iphone 15 là gì"`
**Output**:
```json
{
  "is_question": true,
  "question_type": "what",
  "keyword_type": "mid-tail",
  "commercial_score": 0,
  "serp_features": ["Featured Snippet (Paragraph)"]
}
```
→ **Hành động**: Viết bài định nghĩa ngắn gọn để lên Featured Snippet.

### Ví dụ 2: Từ khóa How-to
**Input**: `"cách chụp màn hình iphone 15"`
**Output**:
```json
{
  "is_question": true,
  "question_type": "how",
  "keyword_type": "long-tail",
  "commercial_score": 0,
  "serp_features": ["Featured Snippet (Steps)", "Video Pack"]
}
```
→ **Hành động**: Viết hướng dẫn từng bước + làm video.

### Ví dụ 3: Từ khóa thương mại cao
**Input**: `"mua iphone 15 giá rẻ"`
**Output**:
```json
{
  "is_question": false,
  "keyword_type": "long-tail",
  "commercial_score": 80,
  "difficulty": 40,
  "serp_features": ["Shopping Ads"]
}
```
→ **Hành động**: Tạo Landing Page bán hàng, ưu tiên cao vì dễ chuyển đổi.

## 5. Lưu ý khi test

1. **Số lượng từ khóa**: Nên test với ít nhất **15-20 từ khóa** để thấy rõ các cluster và related keywords.
2. **Thời gian xử lý**: Với 20 keywords, API sẽ mất khoảng 2-5 giây.
3. **Nếu gặp lỗi**: Kiểm tra lại API Key và đảm bảo server đang chạy.

## 6. So sánh trước và sau nâng cấp

| Trường | Trước | Sau |
|---|---|---|
| `matching_point` | 0.85 | 85.0 |
| `is_question` | ❌ Không có | ✅ true/false |
| `question_type` | ❌ Không có | ✅ "what"/"how"... |
| `keyword_type` | ❌ Không có | ✅ "long-tail" |
| `commercial_score` | ❌ Không có | ✅ 0-100 |
| `content_format` | ❌ Không có | ✅ "How-to Guide" |
| `related_keywords` | ❌ Không có | ✅ ["từ 1", "từ 2"...] |
| `avg_commercial_score` | ❌ Không có | ✅ 76.7 |

---

**Chúc anh test thành công! 🎉**
