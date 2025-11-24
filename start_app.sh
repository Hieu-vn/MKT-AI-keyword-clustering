#!/bin/bash
# Script khởi động nhanh hệ thống MKT Keyword AI

echo "🚀 Đang khởi động hệ thống MKT Keyword AI..."

# Kiểm tra Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Lỗi: Docker chưa được cài đặt."
    exit 1
fi

# Pull model trước (để tránh timeout khi start)
echo "📥 Đang tải model Qwen/Qwen2.5-32B-Instruct (có thể mất vài phút)..."
docker pull qwen/qwen2.5-32b-instruct

# Khởi động services
echo "🔄 Đang khởi động containers..."
docker-compose up -d

echo "✅ Hệ thống đã khởi động thành công!"
echo "------------------------------------------------"
echo "📡 API Endpoint: http://localhost:8001"
echo "🔑 API Key Management: python3 keyword_cluster_app/manage_keys.py"
echo "📄 Tài liệu: xem file API_DOCS.md"
echo "------------------------------------------------"
