# Similarity Metric Update

## Problem
Similarity metric trong CSV trước đây được tính dựa trên **centroid** của cluster (trung bình embedding của tất cả từ khóa trong nhóm). Điều này không chính xác vì:
- Tên nhóm đã được đặt theo từ khóa có volume cao nhất
- Similarity nên phản ánh độ tương đồng giữa từ khóa với **TÊN NHÓM**, không phải với centroid

## Solution Implemented

### Before:
```python
# Tính similarity với centroid
cluster_embeddings = embeddings[indices]
centroid = np.mean(cluster_embeddings, axis=0, keepdims=True)
sims = cosine_similarity(cluster_embeddings, centroid).flatten()
```

### After:
```python
# Tìm từ khóa chính là tên nhóm (highest volume)
max_vol_in_cluster = max(volumes[i] for i in indices)
name_keyword_idx = None
for i in indices:
    if volumes[i] == max_vol_in_cluster and original_texts[i] == name:
        name_keyword_idx = i
        break

# Tính similarity so với embedding của tên nhóm
if name_keyword_idx is not None:
    name_embedding = embeddings[name_keyword_idx:name_keyword_idx+1]
    cluster_embeddings = embeddings[indices]
    sims = cosine_similarity(cluster_embeddings, name_embedding).flatten()
```

## Results

### Example: Cluster "vioedu"
```csv
Cluster Name,Keyword,Volume,Similarity
vioedu,vioedu,1500000,1.0000      ← Tên nhóm (similarity = 1.0)
vioedu,vioedu lớp 7,720,0.7339    ← So với "vioedu"
```

### Example: Cluster "toan"
```csv
Cluster Name,Keyword,Volume,Similarity
toan,toan,90500,1.0000              ← Tên nhóm
toan,violympic toán,40500,0.3482   ← Thấp vì khác semantic
toan,thuvientoan,170,0.5319        ← Trung bình
```

### Example: Cluster "toán 7"
```csv
Cluster Name,Keyword,Volume,Similarity
toán 7,toán lớp 7,14800,0.9459     ← Cực kỳ tương đồng!
toán 7,bài tập toán 7,1000,0.8847
```

## Benefits

1. ✅ **Consistency**: Similarity phản ánh đúng mối quan hệ với tên nhóm
2. ✅ **Interpretability**: Dễ hiểu - từ nào càng giống tên nhóm thì similarity càng cao
3. ✅ **Meaningful**: Tên nhóm = 1.0, các từ khác so với nó
4. ✅ **Business Value**: Giúp đánh giá mức độ liên quan của từ khóa với chủ đề chính

## Testing Across Levels

Hệ thống hỗ trợ 3 mức độ chi tiết:

### 1. Level "thấp" (Overview)
- **Ít clusters, mỗi cluster lớn**
- `n_neighbors=25`, `n_components=5`, `min_cluster_size=15`
- Phù hợp: Tổng quan nhanh

### 2. Level "trung bình" (Balanced)
- **Cân bằng giữa tổng quan và chi tiết**
- `n_neighbors=10`, `n_components=10`, `min_cluster_size=3`
- Phù hợp: Phân tích thông thường

### 3. Level "cao" (Granular)
- **Nhiều clusters, mỗi cluster nhỏ và cụ thể**
- `n_neighbors=8`, `n_components=8`, `min_cluster_size=2`
- Phù hợp: Phân tích SEO chi tiết, long-tail

### Test Script

Sử dụng `test_all_levels.py` để so sánh 3 levels:

```bash
python test_all_levels.py
```

Kết quả:
- Tạo 6 files: `clustering_{level}_{timestamp}.json` và `.csv` cho mỗi level
- So sánh số lượng clusters, noise, và coverage
- Giúp chọn level phù hợp với mục đích phân tích

## Comparison Example (Dataset "toán" - 1,492 keywords)

| Level | Clusters | Noise | Top 10 Coverage | Characteristic |
|-------|----------|-------|-----------------|----------------|
| **thấp** | ~50-80 | High | ~40-50% | Broad categories |
| **trung bình** | ~150-200 | Medium | ~55-60% | Balanced |
| **cao** | **341** | **10 (0.67%)** | **65.3%** | Highly specific topics |

## Files Modified
- `/data/MKT KeyWord AI/keyword_cluster_app/services/clustering_service.py` (Lines 183-210)

## Conclusion
Similarity metric giờ phản ánh chính xác mối quan hệ giữa từ khóa và TÊN NHÓM (từ khóa có volume cao nhất). Hệ thống hỗ trợ 3 levels để test và chọn mức độ chi tiết phù hợp.
