import os
import pandas as pd
import chardet
from typing import List, Dict, Any, Optional
from keyword_cluster_app.utils.text_processing import parse_volume_value

def detect_file_encoding(path: str, sample_size: int = 4000) -> str:
    """
    Đoán encoding file dùng chardet.
    """
    with open(path, "rb") as f:
        raw = f.read(sample_size)
    result = chardet.detect(raw)
    enc = result.get("encoding") or "utf-8"
    return enc

def load_keywords_from_file(path: str) -> List[Dict[str, Any]]:
    """
    Đọc file keyword CSV hoặc TSV và trả về list gồm text và volume.
    Tự nhận dạng cột Keyword và cột volume theo nhiều tên khác nhau.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    encoding = detect_file_encoding(path)
    sep_candidates = [",", "\t", ";"]

    df: Optional[pd.DataFrame] = None
    found_keyword_col = None
    found_volume_col = None

    keyword_col_aliases = [
        "keyword",
        "keywords",
        "search term",
        "search terms",
        "từ khóa",
    ]
    volume_col_aliases = [
        "avg. monthly searches",
        "average monthly searches",
        "search volume",
        "volume",
        "số lượng tìm kiếm",
    ]

    # Try reading with different separators
    temp_df = None
    for sep in sep_candidates:
        try:
            # Use on_bad_lines='skip' to handle messy CSVs
            temp_df = pd.read_csv(path, sep=sep, encoding=encoding, on_bad_lines='skip')
            lowered_cols = {c.lower(): c for c in temp_df.columns}

            current_keyword_col = None
            for alias in keyword_col_aliases:
                if alias in lowered_cols:
                    current_keyword_col = lowered_cols[alias]
                    break

            current_volume_col = None
            for alias in volume_col_aliases:
                if alias in lowered_cols:
                    current_volume_col = lowered_cols[alias]
                    break

            if current_keyword_col:
                df = temp_df
                found_keyword_col = current_keyword_col
                found_volume_col = current_volume_col
                break

        except Exception:
            continue

    if df is None or found_keyword_col is None:
        # Fallback: if temp_df exists but no column matched, show columns
        cols = list(temp_df.columns) if temp_df is not None else "Unknown"
        raise ValueError(
            "Không tìm thấy cột keyword trong file với các dấu phân cách thử nghiệm. "
            f"Các cột hiện có: {cols}"
        )

    keyword_col = found_keyword_col
    volume_col = found_volume_col

    records: List[Dict[str, Any]] = []
    for _, row in df.iterrows():
        text = str(row.get(keyword_col, "")).strip()
        if not text:
            continue

        volume = 0
        if volume_col is not None:
            vol_raw = row.get(volume_col, "")
            volume = parse_volume_value(vol_raw)

        records.append({"text": text, "volume": volume})

    return records
