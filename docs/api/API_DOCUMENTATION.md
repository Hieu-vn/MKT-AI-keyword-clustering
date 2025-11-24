# Keyword Clustering API Documentation

## 1. Overview
API này cung cấp khả năng phân cụm từ khóa (Keyword Clustering) dựa trên ngữ nghĩa (Semantic Clustering) sử dụng AI. Hệ thống tự động nhóm các từ khóa có cùng ý định tìm kiếm vào các cluster, đặt tên cluster theo từ khóa có lượng tìm kiếm (volume) cao nhất, và loại bỏ các từ khóa nhiễu (noise).

## 2. Authentication
*   **Method**: API Key
*   **Header**: `X-API-Key: <your_api_key>`

## 3. Endpoint
*   **URL**: `POST /cluster_keywords_sync`
*   **Description**: Phân cụm từ khóa đồng bộ (trả về kết quả ngay). Giới hạn tối đa 5,000 từ khóa mỗi request.

## 4. Request Structure (Input)

Gửi dữ liệu dưới dạng **JSON**.

### Schema
```json
{
  "keywords": [
    {
      "text": "string (required)",
      "volume": "integer (optional, default: 0)"
    }
  ],
  "level": "string (optional, default: 'cao')",
  "clustering_method": "string (optional, default: 'semantic')"
}
```

### Parameters Detail
| Field | Type | Description |
| :--- | :--- | :--- |
| `keywords` | `List[Object]` | **Bắt buộc**. Danh sách từ khóa cần phân cụm. |
| `keywords[].text` | `String` | Nội dung từ khóa. |
| `keywords[].volume` | `Integer` | Lượng tìm kiếm trung bình tháng. Dùng để xác định tên cluster (từ khóa có volume cao nhất sẽ được chọn làm tên). |
| `level` | `String` | Mức độ chi tiết của việc phân cụm:<br>- `"thấp"`: Gom nhóm lớn, tổng quan (Category level).<br>- `"trung bình"`: Cân bằng (Topic level).<br>- `"cao"`: Chi tiết, tách nhỏ theo ý định cụ thể (Niche/Intent level). **Khuyên dùng**. |
| `clustering_method` | `String` | Phương pháp phân cụm. Hiện tại chỉ hỗ trợ `"semantic"`. |

### Example Request
```json
{
  "keywords": [
    {"text": "toán lớp 5", "volume": 40500},
    {"text": "bài tập toán lớp 5", "volume": 12100},
    {"text": "giải toán lớp 5", "volume": 8100},
    {"text": "vioedu", "volume": 1500000},
    {"text": "đăng nhập vioedu", "volume": 200000}
  ],
  "level": "cao",
  "clustering_method": "semantic"
}
```

---

## 5. Response Structure (Output)

Trả về kết quả dưới dạng **JSON**.

### Schema
```json
{
  "clusters": {
    "<cluster_name>": {
      "cluster_name": "string",
      "total_volume_topic": "integer",
      "cluster_intent": "string",
      "keywords": [
        {
          "text": "string",
          "volume": "integer",
          "matching_point": "float"
        }
      ]
    }
  },
  "unclustered_keywords": [],
  "summary": {
    "total_keywords_processed": "integer",
    "total_clusters_found": "integer",
    "noise_keywords_found": "integer",
    "noise_volume": "integer",
    "top10_cluster_volume_percent": "float"
  }
}
```

### Fields Detail

#### `clusters` (Dictionary)
Chứa danh sách các cụm từ khóa đã được phân loại. Key của dictionary chính là tên cluster.

*   **`cluster_name`** (`String`): Tên đại diện của nhóm (là từ khóa có volume cao nhất trong nhóm).
*   **`total_volume_topic`** (`Integer`): Tổng lượng tìm kiếm (volume) của tất cả từ khóa trong nhóm.
*   **`cluster_intent`** (`String`): Ý định tìm kiếm chủ đạo của nhóm (ví dụ: `INFORMATIONAL`, `TRANSACTIONAL`, `NAVIGATIONAL`, hoặc `UNCATEGORIZED`).
*   **`keywords`** (`List[Object]`): Danh sách các từ khóa thuộc nhóm này.
    *   `text` (`String`): Nội dung từ khóa.
    *   `volume` (`Integer`): Volume của từ khóa.
    *   `matching_point` (`Float`): Điểm tương đồng ngữ nghĩa so với tên nhóm (Cluster Name).
        *   Giá trị từ `0.0` đến `1.0`.
        *   `1.0`: Chính là từ khóa tên nhóm.
        *   Càng gần 1.0 thì ngữ nghĩa càng sát với tên nhóm.

#### `summary` (Object)
Thống kê tổng quan về kết quả phân cụm.
*   `total_keywords_processed`: Tổng số từ khóa đầu vào.
*   `total_clusters_found`: Số lượng nhóm tạo ra.
*   `noise_keywords_found`: Số lượng từ khóa nhiễu (không thể phân nhóm hoặc tạo thành nhóm riêng lẻ).
*   `noise_volume`: Tổng volume của các từ khóa nhiễu.
*   `top10_cluster_volume_percent`: % volume mà Top 10 nhóm lớn nhất chiếm giữ (để đánh giá độ tập trung của thị trường).

### Example Response
```json
{
  "clusters": {
    "toán lớp 5": {
      "cluster_name": "toán lớp 5",
      "total_volume_topic": 60700,
      "cluster_intent": "INFORMATIONAL",
      "keywords": [
        {
          "text": "toán lớp 5",
          "volume": 40500,
          "matching_point": 1.0
        },
        {
          "text": "bài tập toán lớp 5",
          "volume": 12100,
          "matching_point": 0.94
        },
        {
          "text": "giải toán lớp 5",
          "volume": 8100,
          "matching_point": 0.92
        }
      ]
    },
    "vioedu": {
      "cluster_name": "vioedu",
      "total_volume_topic": 1700000,
      "cluster_intent": "NAVIGATIONAL",
      "keywords": [
        {
          "text": "vioedu",
          "volume": 1500000,
          "matching_point": 1.0
        },
        {
          "text": "đăng nhập vioedu",
          "volume": 200000,
          "matching_point": 0.85
        }
      ]
    }
  },
  "unclustered_keywords": [],
  "summary": {
    "total_keywords_processed": 5,
    "total_clusters_found": 2,
    "noise_keywords_found": 0,
    "noise_volume": 0,
    "top10_cluster_volume_percent": 100.0
  }
}
```

## 6. Error Codes
*   `200 OK`: Thành công.
*   `400 Bad Request`: Dữ liệu đầu vào không hợp lệ (ví dụ: thiếu trường `keywords`, sai định dạng JSON).
*   `403 Forbidden`: Sai API Key.
*   `422 Unprocessable Entity`: Lỗi validate dữ liệu (ví dụ: volume không phải số).
*   `500 Internal Server Error`: Lỗi hệ thống.
