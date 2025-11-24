# Tài liệu kết nối API Keyword Clustering

## 1. Thông tin kết nối
- **Base URL**: `http://<IP_HOAC_DOMAIN_CUA_BAN>:8000`
- **Authentication**: Sử dụng Header `X-API-Key` để xác thực.

### API Key (Dành cho đối tác):
```
sk-25d71a183b2b0aa9e0c99de4d1d04bd2
```

## 2. Các Endpoint chính

### A. Phân cụm từ khóa (Đồng bộ - Sync)
Dùng cho số lượng từ khóa nhỏ (dưới 1000 từ), trả về kết quả ngay lập tức.

- **URL**: `/cluster_keywords_sync`
- **Method**: `POST`
- **Headers**:
  - `Content-Type`: `application/json`
  - `X-API-Key`: `sk-25d71a183b2b0aa9e0c99de4d1d04bd2`

**Body Request (JSON):**
```json
{
  "keywords": [
    {"text": "máy pha cà phê", "volume": 1000},
    {"text": "cách pha cà phê ngon", "volume": 500},
    {"text": "mua máy pha cà phê ở đâu", "volume": 200}
  ],
  "level": "trung bình", 
  "clustering_method": "semantic"
}
```
*Note: `level` có thể là "thấp", "trung bình", "cao". `clustering_method` là "semantic" hoặc "serp".*

**Response Success (200 OK):**
```json
{
  "clusters": {
    "Máy pha cà phê": {
      "cluster_name": "Máy pha cà phê",
      "keywords": [
        {"text": "máy pha cà phê", "volume": 1000, "matching_point": 100.0},
        {"text": "mua máy pha cà phê ở đâu", "volume": 200, "matching_point": 95.5}
      ],
      "total_volume_topic": 1200
    },
    "Cách pha cà phê": {
      "cluster_name": "Cách pha cà phê",
      "keywords": [
        {"text": "cách pha cà phê ngon", "volume": 500, "matching_point": 100.0}
      ],
      "total_volume_topic": 500
    }
  },
  "unclustered_keywords": [],
  "summary": {
    "total_keywords_processed": 3,
    "total_clusters_found": 2
  }
}
```

---

### B. Phân cụm từ khóa (Bất đồng bộ - Async)
Dùng cho số lượng từ khóa lớn, xử lý nền.

- **URL**: `/cluster_keywords`
- **Method**: `POST`
- **Headers**: Giống như trên.
- **Body**: Giống như endpoint Sync.

**Response (202 Accepted):**
```json
{
  "task_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
  "status": "pending",
  "message": "Clustering task submitted successfully. Use /results/{task_id} to check status."
}
```

### C. Lấy kết quả (Async)
Kiểm tra trạng thái và lấy kết quả của task bất đồng bộ.

- **URL**: `/results/{task_id}`
- **Method**: `GET`
- **Headers**: Cần có `X-API-Key`.

**Response khi đang xử lý:**
```json
{
  "task_id": "...",
  "status": "in_progress",
  "progress": "50%",
  "message": "Task is still processing."
}
```

**Response khi hoàn thành:**
Trả về cấu trúc tương tự như endpoint Sync (kèm trường `result`).
