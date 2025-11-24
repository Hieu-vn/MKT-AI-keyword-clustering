# Hướng Dẫn Test API Bằng Postman

Tài liệu này hướng dẫn chi tiết cách kiểm tra API Phân Cụm Từ Khóa bằng công cụ Postman.

## 1. Thông Tin Cấu Hình
*   **Server IP**: `172.16.120.23`
*   **Port**: `8001`
*   **API Key**: `sk-2631259f7b709b4d7fa370cf86aac259`

---

## 2. Các Bước Thực Hiện Trên Postman

### Bước 1: Tạo Request Mới
1.  Mở Postman.
2.  Nhấn nút **`+`** hoặc **New** để tạo một request mới.
3.  Chọn method là **`POST`** (thay vì GET mặc định).

### Bước 2: Nhập URL
Nhập địa chỉ sau vào thanh địa chỉ (URL bar):
```text
http://172.16.120.23:8001/cluster_keywords_sync
```

### Bước 3: Cấu Hình Headers
Chuyển sang tab **Headers** (ngay dưới thanh URL) và thêm 2 dòng sau:

| Key | Value |
| :--- | :--- |
| `Content-Type` | `application/json` |
| `X-API-Key` | `sk-2631259f7b709b4d7fa370cf86aac259` |

### Bước 4: Nhập Dữ Liệu (Body)
1.  Chuyển sang tab **Body**.
2.  Chọn tùy chọn **raw**.
3.  Ở menu thả xuống bên phải (thường là Text), chọn **JSON**.
4.  Copy và paste đoạn JSON mẫu dưới đây vào khung soạn thảo:

```json
{
  "keywords": [
    {"text": "toán lớp 5", "volume": 5000},
    {"text": "bài tập toán lớp 5", "volume": 2000},
    {"text": "giải toán lớp 5", "volume": 1500},
    {"text": "sách giáo khoa toán 5", "volume": 1000},
    {"text": "vioedu", "volume": 100000},
    {"text": "đăng nhập vioedu", "volume": 50000},
    {"text": "thi vioedu", "volume": 15000}
  ],
  "level": "cao",
  "clustering_method": "semantic"
}
```

### Bước 5: Gửi Request
1.  Nhấn nút **Send** màu xanh dương.
2.  Đợi khoảng 1-3 giây.

### Bước 6: Kiểm Tra Kết Quả
Ở phần **Response** phía dưới, bạn sẽ thấy:
*   **Status**: `200 OK`
*   **Body**: Dữ liệu JSON trả về chứa các cụm từ khóa đã được phân loại (ví dụ: cụm "vioedu", cụm "toán lớp 5").

---

## 3. Xử Lý Lỗi Thường Gặp

*   **Lỗi `Could not validate credentials` (403 Forbidden)**:
    *   Kiểm tra lại `X-API-Key` trong tab Headers xem có bị thừa khoảng trắng không.
*   **Lỗi `Connection Refused` hoặc `Timeout`**:
    *   Kiểm tra xem máy tính của bạn có kết nối được tới IP `172.16.120.23` không (thử ping).
    *   Đảm bảo port `8001` đã được mở trên server.
*   **Lỗi `400 Bad Request`**:
    *   Kiểm tra lại cú pháp JSON trong tab Body (ví dụ: thiếu dấu phẩy, ngoặc kép).
