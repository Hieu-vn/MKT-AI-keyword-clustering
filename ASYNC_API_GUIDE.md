# Tài liệu Tích hợp API Phân cụm Từ khóa (Asynchronous)

## 1. Tổng quan (Overview)
Hệ thống cung cấp giao diện API bất đồng bộ (Asynchronous API) được thiết kế chuyên biệt cho việc xử lý các tập dữ liệu từ khóa quy mô lớn (Big Data). Kiến trúc này sử dụng cơ chế **Task Queue** để đảm bảo hiệu năng cao, độ ổn định và khả năng mở rộng (Scalability) khi thực hiện các thuật toán AI phức tạp.

**Luồng xử lý (Workflow):**
1.  **Submission**: Client gửi tập dữ liệu đầu vào -> Server xác nhận và trả về `task_id`.
2.  **Processing**: Hệ thống thực hiện phân cụm ngữ nghĩa trong nền (Background Processing).
3.  **Polling**: Client định kỳ kiểm tra trạng thái thông qua `task_id` để nhận kết quả cuối cùng.

## 2. Cấu hình Kết nối (Connection Config)

*   **Base URL**: `http://172.16.120.23:8001`
*   **Authentication**: Bảo mật qua Header.
    *   Header Name: `X-API-Key`
    *   Value: `sk-25d71a183b2b0aa9e0c99de4d1d04bd2`

---

## 3. Chi tiết Endpoints

### A. Khởi tạo Tác vụ (Submit Task)
Endpoint này tiếp nhận dữ liệu và đẩy vào hàng đợi xử lý.

*   **Method**: `POST`
*   **Endpoint**: `/cluster_keywords`
*   **Full URL**: `http://172.16.120.23:8001/cluster_keywords`
*   **Content-Type**: `application/json`

**Cấu trúc Request (Body Schema):**

| Trường (Field) | Kiểu dữ liệu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `keywords` | Array[Object] | **Có** | Danh sách các từ khóa cần xử lý. |
| `keywords[].text` | String | **Có** | Nội dung từ khóa. |
| `keywords[].volume` | Integer | Không | Volume tìm kiếm (Mặc định: 0). |
| `level` | String | Không | Độ chi tiết phân cụm: `thấp`, `trung bình` (mặc định), `cao`. |
| `clustering_method` | String | Không | Thuật toán: `semantic` (mặc định) hoặc `serp`. |

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

**Mẫu Response (HTTP 202 Accepted):**
```json
{
  "task_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
  "status": "pending",
  "message": "Clustering task submitted successfully."
}
```

---

### B. Tra cứu Kết quả (Retrieve Results)
Endpoint này dùng để kiểm tra trạng thái xử lý và lấy kết quả đầu ra.

*   **Method**: `GET`
*   **Endpoint**: `/results/{task_id}`
*   **Full URL**: `http://172.16.120.23:8001/results/{task_id}`

**Các trạng thái phản hồi (Response States):**

**1. Đang xử lý (In Progress)**
Hệ thống đang thực hiện phân tích. Client nên đợi một khoảng thời gian (Backoff strategy) trước khi gọi lại.
```json
{
  "task_id": "d290f1ee-...",
  "status": "in_progress",
  "progress": "45%",
  "message": "Task is still processing."
}
```

**2. Hoàn thành (Completed)**
Tác vụ đã xong, kết quả chi tiết nằm trong trường `result`.
```json
{
  "task_id": "d290f1ee-...",
  "status": "completed",
  "result": {
      "clusters": { 
          "Tên Cụm": {
              "cluster_name": "...",
              "keywords": [ ... ],
              "total_volume_topic": 1500
          }
      },
      "unclustered_keywords": [ ... ],
      "summary": {
          "total_keywords_processed": 100,
          "total_clusters_found": 10
      }
  }
}
```

**3. Thất bại (Failed)**
Có lỗi xảy ra trong quá trình xử lý.
```json
{
  "task_id": "d290f1ee-...",
  "status": "failed",
  "error": "Mô tả chi tiết lỗi..."
}
```
