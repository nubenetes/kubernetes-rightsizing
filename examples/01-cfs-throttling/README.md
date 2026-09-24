# Example 01: Linux CFS Quota Throttling Lab

This lab provides hands-on reproduction manifests demonstrating how rigid container CPU limits create artificial latency spikes due to Linux Completely Fair Scheduler (CFS) quota exhaustion.

## Manifests

### 1. `deployment-throttled.yaml` (Anti-Pattern)
Enforces a tight CPU limit (`cpu: "500m"`) on a multi-threaded workload. Under concurrent load, the kernel freezes the container for the remainder of each 100ms CFS quota period, resulting in severe P99 latency degradation.

### 2. `deployment-unthrottled.yaml` (Best Practice)
Provides an adequate CPU request (`cpu: "1000m"`) for scheduling priority, but omits the hard CPU limit. The workload can freely burst across available node cycles without experiencing CFS throttling.

---

## Running the Benchmark

1. Deploy the throttled deployment:
   ```bash
   kubectl apply -f deployment-throttled.yaml
   ```

2. Run the load test script:
   ```bash
   ./load-test.sh http://<POD_IP>:8080
   ```

3. Observe throttling in Prometheus:
   ```promql
   rate(container_cpu_cfs_throttled_periods_total[1m])
   ```

4. Deploy the unthrottled deployment and repeat the benchmark:
   ```bash
   kubectl apply -f deployment-unthrottled.yaml
   ```
