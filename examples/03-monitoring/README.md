# Monitoring & Prometheus Alerting Lab

Provides production-ready Prometheus alerts and PromQL diagnostic queries for rightsizing detection.

## Included Resources:
1. `prometheus-rules.yaml`: PrometheusRule Custom Resource defining alerts for:
   - `K8sContainerCPUThrottlingHigh`
   - `K8sContainerMemoryApproachingLimit`
   - `K8sPodOOMKilled`
   - `K8sWorkloadOverprovisioned`
2. `promql-cheat-sheet.md`: Rapid diagnostic query collection for capacity review.
