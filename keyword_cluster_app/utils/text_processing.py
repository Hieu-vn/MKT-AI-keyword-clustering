import re
from typing import Any, List, Dict
import numpy as np
import math

def clean_keyword(text: str) -> str:
    """
    Chuẩn hóa từ khóa:
    - Chuyển về chữ thường.
    - Xóa khoảng trắng thừa.
    - Chuẩn hóa các mẫu câu đặc thù (giáo dục).
    """
    if not isinstance(text, str):
        return ""
    
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    
    # Chuẩn hóa lớp, tập, trang – cực kỳ quan trọng với giáo dục VN
    text = re.sub(r'lớp\s*(\d+)', r'lớp \1', text)
    text = re.sub(r'tập\s*(\d+)', r'tập \1', text)
    text = re.sub(r'trang\s*(\d+)', r'trang \1', text)
    text = re.sub(r'bài\s*(\d+)', r'bài \1', text)
    
    return text.strip()

def parse_volume_value(value: Any) -> int:
    """
    Chuẩn hóa dữ liệu volume về số nguyên dương.
    Hỗ trợ cả chuỗi có dấu phẩy, số thực, hoặc giá trị NaN.
    """
    if value is None:
        return 0
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        if math.isnan(value):
            return 0
        return int(value)

    value_str = str(value).strip()
    if not value_str:
        return 0

    normalized = value_str.replace(",", "").replace(" ", "")
    try:
        return int(float(normalized))
    except ValueError:
        digits = re.findall(r"\d+", value_str)
        if digits:
            try:
                return int("".join(digits))
            except ValueError:
                return 0
    return 0
