import os 
import time 
from pathlib import Path 

import numpy as np 
import pandas as pd 
import requests 

PROJECT_ROOT = Path(__file__).resolve().parents[1] 
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")
LIMIT = 5 
WARMUP_REQUESTS = 10 
MEASURED_REQUESTS = 100 
TIMEOUT_SECONDS = 60 

QUERIES = [
    "red handbag",
    "black handbag",
    "blue phone case",
    "transparent phone case",
    "black sandals",
    "brown boots",
    "red shoes",
    "dining chair",
    "wooden table",
    "gray sofa",
    "small crossbody bag",
    "comfortable running shoes",
    "black leather handbag",
    "white bed pillows",
    "navy blue chair",
    "clear phone case",
    "waterproof sandals",
    "modern metal furniture",
    "bedroom wall decor",
    "large living room sofa",
    "chair for dining room",
    "sofa for living room",
    "shoes for running",
    "phone protection case",
    "storage cabinet for bedroom",
    "decorative lighting for home",
    "bag for everyday use",
    "sandals for summer",
    "furniture for small apartment",
    "wall art for bedroom",
    "cozy bedroom vibe",
    "minimalist workspace",
    "rustic living room",
    "elegant evening bag",
    "modern office setup",
    "warm neutral home decor",
    "vintage inspired furniture",
    "calm relaxing bedroom",
    "playful colorful style",
    "luxurious fashion accessory",
]

def wait_for_api(session: requests.Session) -> None: 
    for attempt in range(30): 
        try: 
            response = session.get(
                f"{API_URL}/health", 
                timeout=10, 
            )
            response.raise_for_status() 
            print("API is ready.") 
            return 
        except requests.RequestException: 
            if attempt == 29: 
                raise 
            print(f"Waiting for API... attempt {attempt + 1}/30") 
            time.sleep(2)

def run_request(session: requests.Session, query: str) -> dict: 
    request_start = time.perf_counter() 

    response = session.post(
        f"{API_URL}/search", 
        json={
            "query": query, 
            "limit": LIMIT, 
        }, 
        timeout=TIMEOUT_SECONDS, 
    )

    response.raise_for_status() 

    return {
        "query": query, 
        "status_code": response.status_code,
        "total_ms": (time.perf_counter() - request_start) * 1000, 
        "result_count": len(response.json()["results"]), 
    }

if __name__ == "__main__": 
    session = requests.Session() 
    session.trust_env = False 

    wait_for_api(session) 

    print(f"API: {API_URL}") 
    print("Running warm-up requests...")  

    for index in range(WARMUP_REQUESTS): 
        query = QUERIES[index % len(QUERIES)]
        run_request(session, query) 

    print(f"Running {MEASURED_REQUESTS} measured requests...") 

    measured_rows = [] 

    for index in range(MEASURED_REQUESTS): 
        query = QUERIES[index % len(QUERIES)] 
        measured_rows.append(run_request(session, query)) 

    benchmark = pd.DataFrame(measured_rows) 
    latencies = benchmark["total_ms"].to_numpy() 

    summary = {
        "warmup_requests": WARMUP_REQUESTS, 
        "measured_requests": MEASURED_REQUESTS, 
        "limit": LIMIT, 
        "mean_ms": float(np.mean(latencies)), 
        "median_p50_ms": float(np.percentile(latencies, 50)), 
        "p95_ms": float(np.percentile(latencies, 95)), 
        "p99_ms": float(np.percentile(latencies, 99)), 
        "min_ms": float(np.min(latencies)), 
        "max_ms": float(np.max(latencies)), 
    }

    print("\nLatency summary:")
    for key, value in summary.items(): 
        print(f"{key}: {value}") 

    output_dir = PROJECT_ROOT / "data" / "evaluation"        
    output_dir.mkdir(parents=True, exist_ok=True) 

    benchmark_path = output_dir / "latency_benchmark.csv"
    summary_path = output_dir / "latency_summary.csv"

    benchmark.to_csv(benchmark_path, index=False) 
    pd.DataFrame([summary]).to_csv(summary_path, index=False) 

    print(f"\nSaved requests: {benchmark_path}")
    print(f"Saved summary: {summary_path}")