# Keyword Clustering API - AI-Powered SEO Tool

> Hệ thống phân cụm từ khóa thông minh sử dụng AI (Semantic Clustering) và phân tích SEO chuyên sâu.

## 📋 Mục lục

- [Tổng quan](#tổng-quan)
- [Tính năng](#tính-năng)
- [Cấu trúc dự án](#cấu-trúc-dự-án)
- [Cài đặt](#cài-đặt)
- [Sử dụng](#sử-dụng)
- [Tài liệu](#tài-liệu)
- [API Reference](#api-reference)

---

## 🎯 Tổng quan

Hệ thống phân cụm từ khóa tự động dựa trên:
- **AI Semantic Analysis**: Sử dụng `vietnamese-bi-encoder` để hiểu ngữ nghĩa tiếng Việt
- **Advanced Clustering**: UMAP + HDBSCAN cho kết quả chính xác
- **SEO Intelligence**: Phân tích ý định tìm kiếm, độ khó, định dạng nội dung

### Điểm mạnh
✅ Xử lý tiếng Việt chuyên sâu  
✅ Phân tích SEO metrics dựa trên chuẩn Ahrefs/Semrush/Moz  
✅ API RESTful dễ tích hợp  
✅ Hỗ trợ 1000+ từ khóa/request  
✅ Kết quả JSON + CSV  

---

## 🚀 Tính năng

### 1. Semantic Clustering
- Gom nhóm từ khóa theo ngữ nghĩa (không chỉ từ giống nhau)
- Tự động đặt tên cluster theo từ khóa có volume cao nhất
- Loại bỏ từ khóa nhiễu (noise)

### 2. SEO Analysis (100% miễn phí)
- **Question Detection**: Phát hiện từ khóa dạng câu hỏi (what/how/why...)
- **Keyword Type**: Phân loại short-tail/mid-tail/long-tail
- **Commercial Intent**: Đánh giá ý định mua hàng (0-100)
- **Difficulty Estimation**: Ước lượng độ khó xếp hạng
- **Content Format**: Gợi ý định dạng bài viết (Listicle, How-to...)
- **Related Keywords**: Trích xuất từ khóa liên quan (LSI)

### 3. Multi-Level Clustering
- **Thấp**: Gom nhóm lớn (Category level)
- **Trung bình**: Cân bằng (Topic level)
- **Cao**: Chi tiết (Niche/Intent level) - Khuyên dùng

---

## 📁 Cấu trúc dự án

```
/data/MKT KeyWord AI/
├── keyword_cluster_app/          # Source code chính (Application)
│   ├── api.py                    # FastAPI App (Main Entry)
│   ├── cli.py                    # CLI Tool (Command Line Interface)
│   ├── worker.py                 # Background Worker
│   ├── services/                 # Business Logic
│   ├── config.py                 # Configuration

# Install dependencies
poetry install

# Run API
poetry run uvicorn keyword_cluster_app.api:app --reload
```

---

## 💻 Sử dụng

### 1. Tạo API Key
```bash
cd keyword_cluster_app
python3 manage_keys.py create "Tên khách hàng"
```

### 2. Test API với cURL
```bash
curl -X POST "http://172.16.120.23:8001/cluster_keywords_sync" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: YOUR_API_KEY" \
     -d '{
       "keywords": [
         {"text": "mua iphone 15", "volume": 10000},
         {"text": "giá iphone 15", "volume": 8000}
       ],
       "level": "cao"
     }'
```

### 3. Test với Postman
Xem hướng dẫn chi tiết: [`docs/guides/POSTMAN_GUIDE.md`](docs/guides/POSTMAN_GUIDE.md)

### 4. Chạy test tự động
```bash
cd scripts/testing
python3 test_all_levels.py
```

---

## 📚 Tài liệu

### API Documentation
- **[API Reference](docs/api/API_DOCUMENTATION.md)**: Mô tả đầy đủ endpoints, request/response
- **[Postman Guide](docs/guides/POSTMAN_GUIDE.md)**: Hướng dẫn test với Postman
- **[Advanced Testing](docs/guides/POSTMAN_TEST_ADVANCED.md)**: Test các tính năng nâng cao

### Kiến thức chuyên môn
- **[SEO Metrics Knowledge Base](docs/knowledge_base/SEO_METRICS_KNOWLEDGE_BASE.md)**: Cơ sở kiến thức SEO từ Ahrefs/Semrush/Moz
- **[Implementation Plan](docs/knowledge_base/IMPLEMENTATION_PLAN_SEO_METRICS.md)**: Kế hoạch triển khai metrics

### Kiến trúc hệ thống
- **[Cluster Naming](docs/architecture/CLUSTER_NAMING_OPTIMIZATION.md)**: Cách đặt tên cluster
- **[Similarity Calculation](docs/architecture/SIMILARITY_UPDATE.md)**: Tính toán độ tương đồng

---

## 🔑 API Reference

### Endpoint chính
```
POST /cluster_keywords_sync
```

### Request
```json
{
  "keywords": [
    {"text": "string", "volume": integer}
  ],
  "level": "thấp" | "trung bình" | "cao",
  "clustering_method": "semantic"
}
```

### Response
```json
{
  "clusters": {
    "cluster_name": {
      "keywords": [
        {
          "text": "string",
          "volume": integer,
          "matching_point": float (0-100),
          "is_question": boolean,
          "question_type": "what" | "how" | "why" | ...,
          "keyword_type": "short-tail" | "mid-tail" | "long-tail",
          "commercial_score": integer (0-100),
          "difficulty": integer (0-100),
          "micro_intent": "string",
          "serp_features": ["string"]
        }
      ],
      "total_volume_topic": integer,
      "cluster_intent": "string",
      "content_format": "string",
      "related_keywords": ["string"],
      "avg_commercial_score": float
    }
  },
  "summary": {
    "total_keywords_processed": integer,
    "total_clusters_found": integer,
    "noise_keywords_found": integer,
    "top10_cluster_volume_percent": float
  }
}
```

Chi tiết: [API_DOCUMENTATION.md](docs/api/API_DOCUMENTATION.md)

---

## 🔐 Quản lý API Keys

### Tạo key mới
```bash
python3 keyword_cluster_app/manage_keys.py create "Client Name"
```

### Xem danh sách keys
```bash
python3 keyword_cluster_app/manage_keys.py list
```

### Thu hồi key
```bash
python3 keyword_cluster_app/manage_keys.py revoke "Client Name"
```

Keys được lưu trong: `keyword_cluster_app/api_keys.json`

---

## 🧪 Testing

### Test với dataset mẫu
```bash
cd scripts/testing
python3 test_all_levels.py
```

### Kết quả test
- JSON: `data/test_results/clustering_*.json`
- CSV: `data/test_results/clustering_*.csv`

---

## 📊 Performance

- **Tốc độ**: ~27 giây cho 1492 keywords (level cao)
- **Độ chính xác**: 252 clusters từ 1492 keywords
- **Noise rate**: <1% (8/1492 keywords)
- **Top 10 coverage**: 65.4% volume

---

## 🤝 Đóng góp

Dự án này được phát triển cho mục đích nội bộ. Nếu có góp ý, vui lòng liên hệ team.

---

## 📝 License

Proprietary - Internal use only

---

## 📞 Liên hệ

- **Server IP**: 172.16.120.23
- **API Port**: 8001
- **Documentation**: Xem thư mục `docs/`

---

**Phiên bản**: 2.0 (Nâng cấp SEO Metrics - Nov 2025)  
**Cập nhật cuối**: 24/11/2025
