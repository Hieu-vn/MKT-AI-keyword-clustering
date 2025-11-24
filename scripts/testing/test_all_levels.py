#!/usr/bin/env python3
"""
Test script to compare clustering results across different levels
"""
import requests
import json
import csv
from datetime import datetime
from collections import Counter

API_URL = "http://localhost:8001/cluster_keywords_sync"
API_KEY = "sk-2631259f7b709b4d7fa370cf86aac259"

def load_keywords(csv_path, max_keywords=None):
    """Load keywords from CSV/TSV"""
    keywords = []
    # Try different encodings to handle various CSV formats
    encodings = ['utf-16', 'utf-8-sig', 'utf-8', 'latin-1']
    
    for encoding in encodings:
        try:
            keywords = []  # Reset for each attempt
            with open(csv_path, 'r', encoding=encoding) as f:
                # Try both tab and comma delimiters
                reader = csv.DictReader(f, delimiter='\t')
                for row in reader:
                    kw = row.get('Keyword', '').strip()
                    # Try different volume column names
                    vol = row.get('Volume', row.get('Avg. monthly searches', '0')).strip().replace(',', '')
                    if kw:
                        try:
                            keywords.append({"text": kw, "volume": int(vol)})
                        except:
                            keywords.append({"text": kw, "volume": 0})
            if keywords:  # Success if we got keywords
                break
        except (UnicodeDecodeError, UnicodeError):
            continue  # Try next encoding
    
    if max_keywords:
        keywords = keywords[:max_keywords]
    
    return keywords

def test_level(level_name, keywords):
    """Test clustering with a specific level"""
    print(f"\n{'='*60}")
    print(f"Testing Level: {level_name.upper()}")
    print(f"{'='*60}")
    
    payload = {
        "keywords": keywords,
        "level": level_name,
        "clustering_method": "semantic"
    }
    
    headers = {"X-API-Key": API_KEY}
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        data = response.json()
        
        # Extract summary
        summary = data.get('summary', {})
        clusters = data.get('clusters', {})
        
        print(f"\n📊 Results for level '{level_name}':")
        print(f"   Total Clusters: {summary.get('total_clusters_found', 0)}")
        print(f"   Noise Keywords: {summary.get('noise_keywords_found', 0)}")
        print(f"   Noise Volume: {summary.get('noise_volume', 0):,}")
        print(f"   Top 10 Coverage: {summary.get('top10_cluster_volume_percent', 0)}%")
        print(f"   Processing Time: {response.elapsed.total_seconds():.2f}s")
        
        # Top 5 clusters by volume
        cluster_list = [(name, info['total_volume_topic']) for name, info in clusters.items()]
        cluster_list.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\n   Top 5 Clusters by Volume:")
        for i, (name, vol) in enumerate(cluster_list[:5], 1):
            cluster_info = clusters[name]
            num_kw = len(cluster_info['keywords'])
            print(f"      {i}. {name}: {vol:,} volume ({num_kw} keywords)")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = f"clustering_{level_name}_{timestamp}.json"
        csv_file = f"clustering_{level_name}_{timestamp}.csv"
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Write CSV
        csv_data = data.get('csv_data', '')
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write(csv_data)
        
        print(f"\n   ✅ Saved: {json_file}")
        print(f"   ✅ Saved: {csv_file}")
        
        return summary
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

if __name__ == "__main__":
    # Load keywords
    csv_path = "/data/MKT KeyWord AI/Keyword Stats 2025-10-21 at 14_55_08 - toán.csv"
    print(f"Loading keywords from: {csv_path}")
    keywords = load_keywords(csv_path)
    print(f"Loaded {len(keywords)} keywords.\n")
    
    # Test all levels
    levels = ["cao"]
    results = {}
    
    for level in levels:
        result = test_level(level, keywords)
        if result:
            results[level] = result
    
    # Comparison summary
    print(f"\n\n{'='*60}")
    print("COMPARISON SUMMARY")
    print(f"{'='*60}")
    print(f"{'Level':<15} {'Clusters':<12} {'Noise':<10} {'Top10%':<10} {'Insight'}")
    print(f"{'-'*60}")
    
    for level in levels:
        if level in results:
            r = results[level]
            clusters = r.get('total_clusters_found', 0)
            noise = r.get('noise_keywords_found', 0)
            top10 = r.get('top10_cluster_volume_percent', 0)
            print(f"{level:<15} {clusters:<12} {noise:<10} {top10:<10.1f}")
    
    print(f"\n✅ All tests completed!")
