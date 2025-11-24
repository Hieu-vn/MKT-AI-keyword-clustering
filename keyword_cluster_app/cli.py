import argparse
import json
import logging
import os
import sys
import logging.handlers
import pandas as pd
from fastapi import FastAPI

from keyword_cluster_app.config import LOG_FILE_PATH
from keyword_cluster_app.model import load_model
from keyword_cluster_app.services.clustering_service import ClusteringService
from keyword_cluster_app.utils.file_io import load_keywords_from_file
from keyword_cluster_app.utils.common import set_seed

app = FastAPI()
logger = logging.getLogger(__name__)

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Cluster keywords from a file into semantic topics "
            "for SEO and content planning."
        )
    )
    parser.add_argument(
        "file_path",
        type=str,
        help="Đường dẫn file CSV hoặc TSV chứa danh sách keyword.",
    )
    parser.add_argument(
        "--level",
        type=str,
        default="trung bình",
        choices=["thấp", "trung bình", "cao"],
        help=(
            "Mức độ chi tiết cụm "
            "thấp = ít cụm, cụm to "
            "trung bình = cân bằng "
            "cao = nhiều cụm nhỏ."
        ),
    )
    parser.add_argument(
        "--min-cluster-size",
        type=int,
        default=None,
        help=(
            "Kích thước cụm tối thiểu cho HDBSCAN. "
            "Nếu không được cung cấp, sẽ sử dụng heuristic tự động điều chỉnh."
        ),
    )
    parser.add_argument(
        "--clustering-method",
        type=str,
        default="semantic",
        choices=["semantic", "serp"],
        help=(
            "Phương pháp phân cụm: 'semantic' (mặc định) dùng embedding, "
            "'serp' dùng dữ liệu SERP (URL overlap)."
        ),
    )
    parser.add_argument(
        "--log-to-stdout",
        action="store_true",
        help="Ghi log ra stdout thay vì file.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Bật chế độ log chi tiết (DEBUG). Mặc định là INFO.",
    )

    args = parser.parse_args()

    # Configure logging based on arguments
    log_level = logging.DEBUG if args.verbose else logging.INFO
    log_format = "%(asctime)s - %(levelname)s - %(message)s"

    if args.log_to_stdout:
        logging.basicConfig(level=log_level, format=log_format, stream=sys.stdout)
    else:
        os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
        # Use RotatingFileHandler for log rotation
        file_handler = logging.handlers.RotatingFileHandler(
            LOG_FILE_PATH, maxBytes=10*1024*1024, backupCount=5 # 10 MB per file, 5 backup files
        )
        file_handler.setFormatter(logging.Formatter(log_format))
        
        # Clear existing handlers to prevent duplicate logs
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        
        logging.basicConfig(level=log_level, handlers=[file_handler])
    
    # Re-initialize logger after basicConfig to apply new settings
    global logger
    logger = logging.getLogger(__name__) 

    try:
        set_seed(42) # Set global seed for reproducibility
        raw_keywords = load_keywords_from_file(args.file_path)

        print("Loading AI model...")
        # Initialize service (which loads model if needed)
        service = ClusteringService()
        print("AI model loaded.")

        print(f"Starting clustering with detail level: {args.level}...")
        results = service.process_clustering(
            raw_keywords,
            level=args.level,
            min_cluster_size_override=args.min_cluster_size,
            clustering_method=args.clustering_method
        )

        # For JSON output, we can exclude the unclustered list as it's not a cluster
        print("\n--- Clustering Results (JSON) ---")
        print(json.dumps(results["clusters"], indent=2, ensure_ascii=False))

        if results["unclustered"]:
            print("\n--- Unclustered Keywords ---")
            for kw in results["unclustered"]:
                print(f"- {kw['original_text']} (Volume: {kw['volume']})")

        print("\n--- Summary ---")
        print(
            f"Total Keywords Processed: "
            f"{results['summary']['total_keywords_processed']}"
        )
        print(
            f"Total Clusters Found: "
            f"{results['summary']['total_clusters_found']}"
        )
        print(
            f"Unclustered (Noise) Keywords: " 
            f"{results['summary']['noise_keywords_found']}"
        )

        print("\n--- CSV Data ---")
        print(results["csv_data"])

        # TỰ ĐỘNG GHI FILE CSV KHI CHẠY CLI
        csv_filename = f"clustering_result_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(csv_filename, 'w', encoding='utf-8') as f:
            f.write(results["csv_data"])
        print(f"\n>>> ĐÃ LƯU KẾT QUẢ RA FILE: {csv_filename}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
