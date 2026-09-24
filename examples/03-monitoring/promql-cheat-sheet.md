# PromQL Rightsizing Diagnostic Cheat-Sheet

## 1. Top 10 Containers with Highest CPU Throttling
```promql
topk(10,
  sum by (namespace, pod, container) (
    rate(container_cpu_cfs_throttled_periods_total{container!=""}[5m])
  )
  /
  sum by (namespace, pod, container) (
    rate(container_cpu_cfs_periods_total{container!=""}[5m])
  ) * 100
)
```

## 2. Pods Overprovisioned on CPU (Using < 20% of Request)
```promql
(
  sum by (namespace, pod, container) (
    rate(container_cpu_usage_seconds_total{container!=""}[1h])
  )
  /
  sum by (namespace, pod, container) (
    kube_pod_container_resource_requests{resource="cpu"}
  )
) * 100 < 20
```

## 3. Pods Overprovisioned on Memory (Using < 30% of Request)
```promql
(
  sum by (namespace, pod, container) (
    container_memory_working_set_bytes{container!=""}
  )
  /
  sum by (namespace, pod, container) (
    kube_pod_container_resource_requests{resource="memory"}
  )
) * 100 < 30
```

## 4. Total Cluster Request Commitment vs. Node Allocatable
```promql
# Cluster-wide CPU Commitment Ratio (> 100% means overcommitted)
sum(kube_pod_container_resource_requests{resource="cpu"})
/
sum(kube_node_status_allocatable{resource="cpu"}) * 100
```
