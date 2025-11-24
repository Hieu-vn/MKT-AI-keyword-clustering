# Keyword Clustering API - Hướng dẫn sử dụng

## Giới thiệu
API phân cụm từ khóa tự động sử dụng AI, tối ưu cho tiếng Việt.

## Thông tin kết nối
- **URL**: `http://172.16.120.23:8001`
- **Endpoint**: `POST /cluster_keywords_sync`
- **API Key**: Liên hệ admin để nhận key

## Cách sử dụng

### 1. Gửi request
```bash
curl -X POST "http://172.16.120.23:8001/cluster_keywords_sync" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "keywords": [
      {"text": "máy pha cà phê", "volume": 1000},
      {"text": "cách pha cà phê", "volume": 500}
    ],
    "level": "cao"
  }'
```

### 2. Nhận kết quả
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
        }
      ],
      "total_volume_topic": 1000
    }
  },
  "summary": {
    "total_keywords_processed": 2,
    "total_clusters_found": 1
  }
}
```

## Tham số

| Tham số | Kiểu | Mô tả |
|---------|------|-------|
| `keywords` | Array | Danh sách từ khóa (bắt buộc) |
| `keywords[].text` | String | Nội dung từ khóa |
| `keywords[].volume` | Integer | Search volume (mặc định: 0) |
| `level` | String | Độ chi tiết: "thấp", "trung bình", "cao" (mặc định: "trung bình") |

## Kết quả trả về

| Trường | Mô tả |
|--------|-------|
| `cluster_name` | Tên cụm (topic) |
| `text` | Từ khóa |
| `volume` | Search volume |
| `matching_point` | Độ liên quan (0-100) |
| `total_volume_topic` | Tổng volume của cụm |

## Liên hệ hỗ trợ
- Email: phamkhachieuforwork1001@gmail.com
