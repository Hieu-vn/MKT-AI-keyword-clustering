# 📋 DANH SÁCH CÔNG VIỆC DỰ ÁN MKT KEYWORD AI

Tài liệu này tổng hợp toàn bộ các hạng mục công việc (tasks) đã được triển khai và hoàn thiện trong dự án **MKT Keyword AI**.

---

## 1. Cơ Sở Hạ Tầng & Môi Trường (Infrastructure)
- [x] **Thiết lập cấu trúc dự án**: Khởi tạo project với Poetry, cấu hình `pyproject.toml` quản lý dependencies.
- [x] **Docker hóa ứng dụng**:
    - Viết `Dockerfile` tối ưu cho Python 3.11.
    - Xây dựng `docker-compose.yml` để orchestrate 4 services: API, Worker, Redis, vLLM.
    - Cấu hình GPU Passthrough cho Docker để tận dụng sức mạnh phần cứng.
- [x] **Tích hợp Redis**: Cài đặt Redis làm Message Broker cho hàng đợi xử lý (Task Queue) và Caching.
- [x] **Tích hợp vLLM**: Triển khai mô hình ngôn ngữ lớn `Qwen/Qwen2.5-32B-Instruct` chạy local qua Docker để xử lý ngôn ngữ tự nhiên tốc độ cao.
- [x] **Script quản trị**:
    - Viết script `start_app.sh` để khởi động nhanh hệ thống 1-click.
    - Viết script `manage_keys.py` để quản lý API Key (CRUD).

## 2. Backend & API (FastAPI)
- [x] **Khởi tạo FastAPI App**: Cấu hình cơ bản, Middleware, CORS, Logging.
- [x] **Xây dựng Endpoints**:
    - `POST /cluster_keywords_sync`: Endpoint xử lý đồng bộ cho request nhỏ (<1000 từ).
    - `POST /cluster_keywords`: Endpoint xử lý bất đồng bộ (Async) cho request lớn.
    - `GET /results/{task_id}`: Endpoint kiểm tra trạng thái và lấy kết quả task background.
    - `GET /health`: Endpoint kiểm tra sức khỏe hệ thống.
- [x] **Cơ chế xác thực (Authentication)**: Middleware kiểm tra `X-API-Key` từ Header.
- [x] **Rate Limiting**: Tích hợp `slowapi` để giới hạn số lượng request (tránh spam/DDoS).
- [x] **Background Worker**: Sử dụng thư viện `arq` để xử lý các tác vụ phân cụm nặng trong nền.

## 3. Core Logic - AI & Clustering
- [x] **Xử lý ngôn ngữ (NLP)**:
    - Tích hợp model `vietnamese-bi-encoder` để chuyển đổi từ khóa sang vector (Embedding).
    - Xây dựng hàm làm sạch từ khóa (`clean_keyword`).
- [x] **Thuật toán Phân cụm (Clustering Engine)**:
    - Tích hợp **UMAP** để giảm chiều dữ liệu vector (tối ưu hóa không gian).
    - Tích hợp **HDBSCAN** để phân cụm mật độ cao.
    - Triển khai logic **Hybrid Clustering**: Kết hợp Semantic (Ngữ nghĩa) + Lexical (Từ vựng/TF-IDF) để tăng độ chính xác.
    - Xử lý nhiễu (Noise Handling): Cơ chế gán lại các từ khóa nhiễu vào cụm gần nhất nếu đủ độ tin cậy.
- [x] **Phân tích SEO Chuyên sâu (SEO Intelligence)**:
    - **Intent Analysis**: Phân loại ý định tìm kiếm (Transactional, Informational, Commercial...).
    - **Keyword Type**: Phân loại Short-tail, Mid-tail, Long-tail.
    - **Commercial Score**: Chấm điểm thương mại (0-100) dựa trên từ khóa mua bán.
    - **Difficulty Estimation**: Ước lượng độ khó từ khóa (KD).
    - **Content Suggestion**: Gợi ý định dạng bài viết phù hợp (Listicle, How-to, Product Page...).
    - **Question Detection**: Phát hiện và phân loại câu hỏi (What, How, Why...).
- [x] **Cross-Encoder Refinement**: Sử dụng Cross-Encoder để kiểm tra lại độ chính xác của từng cụm sau khi phân nhóm.

## 4. Công Cụ Dòng Lệnh (CLI)
- [x] **CLI Tool (`cli.py`)**: Công cụ chạy phân cụm trực tiếp từ terminal không cần qua API.
- [x] **File Processing**: Đọc/Ghi file CSV, xử lý dữ liệu đầu vào/đầu ra.

## 5. Tài Liệu & Hướng Dẫn (Documentation)
- [x] **API Documentation**:
    - Viết `API_DOCS.md`: Hướng dẫn kết nối nhanh cho đối tác.
    - Viết `docs/api/API_DOCUMENTATION.md`: Tài liệu kỹ thuật chi tiết.
- [x] **Kiến thức chuyên môn**:
    - `SEO_METRICS_KNOWLEDGE_BASE.md`: Cơ sở lý thuyết về các chỉ số SEO.
    - `CLUSTER_NAMING_OPTIMIZATION.md`: Giải thích thuật toán đặt tên cụm.
- [x] **Hướng dẫn sử dụng**: `README.md` tổng quan dự án.

## 6. Testing & QA
- [x] **Unit Tests**: Cấu trúc thư mục tests.
- [x] **Integration Tests**: Script `scripts/testing/test_all_levels.py` để chạy thử nghiệm tự động trên 3 cấp độ phân cụm.
- [x] **Performance Tuning**: Tối ưu tham số UMAP/HDBSCAN cho các kích thước dữ liệu khác nhau.

---
*Cập nhật lần cuối: 24/11/2025*
