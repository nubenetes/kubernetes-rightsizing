#!/usr/bin/env bash
set -euo pipefail

TARGET_URL="${1:-http://localhost:8080}"
CONCURRENCY=50
DURATION=30s

echo "=========================================================="
echo "Starting CFS Throttling Benchmark against: $TARGET_URL"
echo "Concurrency: $CONCURRENCY | Duration: $DURATION"
echo "=========================================================="

if command -v hey &>/dev/null; then
    hey -c "$CONCURRENCY" -z "$DURATION" "$TARGET_URL"
elif command -v wrk &>/dev/null; then
    wrk -t 4 -c "$CONCURRENCY" -d "$DURATION" --latency "$TARGET_URL"
else
    echo "Neither 'hey' nor 'wrk' found. Executing concurrent curl benchmark via python3..."
    python3 -c "
import urllib.request, time, concurrent.futures

url = '$TARGET_URL'
def fetch(_):
    start = time.time()
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            return time.time() - start, r.status
    except Exception as e:
        return time.time() - start, str(e)

with concurrent.futures.ThreadPoolExecutor(max_workers=$CONCURRENCY) as executor:
    futures = [executor.submit(fetch, i) for i in range(2000)]
    latencies = [f.result()[0] * 1000 for f in concurrent.futures.as_completed(futures)]

latencies.sort()
print(f'Requests: {len(latencies)}')
print(f'P50 Latency: {latencies[int(len(latencies)*0.50)]:.2f} ms')
print(f'P90 Latency: {latencies[int(len(latencies)*0.90)]:.2f} ms')
print(f'P99 Latency: {latencies[int(len(latencies)*0.99)]:.2f} ms')
"
fi
