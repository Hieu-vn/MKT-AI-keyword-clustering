# Tài liệu dự án - Index

> Danh mục đầy đủ các tài liệu kỹ thuật và hướng dẫn sử dụng

## 📖 Mục lục

### 1. API Documentation
Tài liệu về API endpoints, request/response format

- **[API_DOCUMENTATION.md](api/API_DOCUMENTATION.md)**
  - Mô tả đầy đủ API endpoints
  - Request/Response schema
  - Ví dụ sử dụng
  - Error handling

### 2. Guides (Hướng dẫn sử dụng)
Hướng dẫn từng bước cho người dùng

- **[POSTMAN_GUIDE.md](guides/POSTMAN_GUIDE.md)**
  - Hướng dẫn test API với Postman
  - Cấu hình Headers, Body
  - Ví dụ request cơ bản

- **[POSTMAN_TEST_ADVANCED.md](guides/POSTMAN_TEST_ADVANCED.md)**
  - Test các tính năng SEO nâng cao
  - Dataset mẫu 22 keywords
  - Giải thích kết quả chi tiết

### 3. Knowledge Base (Cơ sở kiến thức)
Kiến thức chuyên môn SEO và thuật toán

- **[SEO_METRICS_KNOWLEDGE_BASE.md](knowledge_base/SEO_METRICS_KNOWLEDGE_BASE.md)**
  - Tổng hợp kiến thức từ Ahrefs, Semrush, Moz
  - Công thức tính toán các metrics
  - Nguồn tham khảo và độ tin cậy
  - **Nội dung**:
    - Keyword Difficulty
    - Commercial Intent / CPC
    - SERP Features
    - Content Format
    - Keyword Type
    - Question Keywords
    - Cluster Metrics

- **[IMPLEMENTATION_PLAN_SEO_METRICS.md](knowledge_base/IMPLEMENTATION_PLAN_SEO_METRICS.md)**
  - Kế hoạch triển khai metrics
  - So sánh logic cũ vs mới
  - Code mẫu chi tiết
  - Roadmap thực hiện

### 4. Architecture (Kiến trúc hệ thống)
Tài liệu kỹ thuật về thiết kế hệ thống

- **[CLUSTER_NAMING_OPTIMIZATION.md](architecture/CLUSTER_NAMING_OPTIMIZATION.md)**
  - Chiến lược đặt tên cluster
  - Từ TF-IDF sang Highest Volume
  - Lý do thay đổi

- **[SIMILARITY_UPDATE.md](architecture/SIMILARITY_UPDATE.md)**
  - Cách tính matching_point
  - Từ cosine similarity sang cluster centroid
  - Ý nghĩa của điểm số

---

## 🎯 Lộ trình đọc tài liệu

### Cho người mới
1. Đọc [README.md](../README.md) - Tổng quan dự án
2. Đọc [POSTMAN_GUIDE.md](guides/POSTMAN_GUIDE.md) - Test API cơ bản
3. Đọc [API_DOCUMENTATION.md](api/API_DOCUMENTATION.md) - Hiểu API

### Cho Developer
1. Đọc [Architecture docs](architecture/) - Hiểu kiến trúc
2. Đọc [SEO_METRICS_KNOWLEDGE_BASE.md](knowledge_base/SEO_METRICS_KNOWLEDGE_BASE.md) - Hiểu logic
3. Đọc [IMPLEMENTATION_PLAN_SEO_METRICS.md](knowledge_base/IMPLEMENTATION_PLAN_SEO_METRICS.md) - Triển khai

### Cho SEO Specialist
1. Đọc [SEO_METRICS_KNOWLEDGE_BASE.md](knowledge_base/SEO_METRICS_KNOWLEDGE_BASE.md) - Kiến thức SEO
2. Đọc [POSTMAN_TEST_ADVANCED.md](guides/POSTMAN_TEST_ADVANCED.md) - Test nâng cao
3. Đọc [API_DOCUMENTATION.md](api/API_DOCUMENTATION.md) - Hiểu output

---

## 📝 Cập nhật tài liệu

Khi thêm tài liệu mới, cập nhật file này và [README.md](../README.md)

**Cập nhật cuối**: 22/11/2025
