# Tài liệu Tích hợp API Phân cụm Từ khóa (Synchronous)

## 1. Tổng quan (Overview)
Hệ thống cung cấp giao diện API đồng bộ (Synchronous API) cho phép nhận kết quả phân cụm ngay lập tức trong một lần gọi (Single Request-Response). Cơ chế này giúp đơn giản hóa quá trình tích hợp, Client không cần thực hiện polling kiểm tra trạng thái.

**Lưu ý quan trọng**:
*   Thời gian phản hồi phụ thuộc vào số lượng từ khóa.
*   Khuyến nghị gửi dưới **5,000 từ khóa/request** để đảm bảo tốc độ tốt nhất (< 30 giây).

## 2. Cấu hình Kết nối (Connection Config)

*   **Base URL**: `http://172.16.120.23:8001`
*   **Authentication**: Bảo mật qua Header.
    *   Header Name: `X-API-Key`
    *   Value: `sk-2631259f7b709b4d7fa370cf86aac259`

---

## 3. Chi tiết Endpoint

### Phân cụm và Nhận kết quả (Cluster & Get Results)
Endpoint này tiếp nhận dữ liệu, xử lý và trả về kết quả phân cụm ngay trong response.

*   **Method**: `POST`
*   **Endpoint**: `/cluster_keywords_sync`
*   **Full URL**: `http://172.16.120.23:8001/cluster_keywords_sync`
*   **Content-Type**: `application/json`

**Cấu trúc Request (Body Schema):**

| Trường (Field) | Kiểu dữ liệu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `keywords` | Array[Object] | **Có** | Danh sách các từ khóa cần xử lý. |
| `keywords[].text` | String | **Có** | Nội dung từ khóa. |
| `keywords[].volume` | Integer | Không | Volume tìm kiếm (Mặc định: 0). |
| `level` | String | Không | Độ chi tiết: `thấp`, `trung bình` (mặc định), `cao`. |
| `clustering_method` | String | Không | Thuật toán: `semantic` (mặc định). |

**Mẫu Request (Example):**
```json
{
  "keywords": [
    {"text": "máy pha cà phê", "volume": 1000},
    {"text": "cách sử dụng máy pha", "volume": 500}
  ],
  "level": "cao",
  "clustering_method": "semantic"
}
```

**Mẫu Response Thành công (HTTP 200 OK):**
Kết quả trả về ngay lập tức (Real-time).

```json
{
  "clusters": {
    "Máy pha cà phê": {
      "cluster_name": "Máy pha cà phê",
      "keywords": [
        {
          "text": "máy pha cà phê",
          "volume": 1000,
          "matching_point": 100.0
        },
        {
          "text": "mua máy pha cà phê",
          "volume": 800,
          "matching_point": 95.5
        }
      ],
      "total_volume_topic": 1800
    }
  },
  "unclustered_keywords": [],
  "summary": {
    "total_keywords_processed": 2,
    "total_clusters_found": 1,
    "noise_keywords_found": 0
  }
}
```

**Mẫu Response Lỗi (HTTP 4xx/5xx):**
```json
{
  "detail": "Mô tả lỗi cụ thể (ví dụ: Quá số lượng từ khóa cho phép)"
}
```
