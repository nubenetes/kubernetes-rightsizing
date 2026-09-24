# Recommendation Engines Lab (KRR & VPA)

Demonstrates configuring **Robusta KRR** and the **Kubernetes Vertical Pod Autoscaler (VPA)**.

## Included Manifests:
1. `krr-config.yaml`: Robusta KRR deployment values, setting Prometheus endpoints and conservative calculation strategies.
2. `vpa-workload.yaml`: VerticalPodAutoscaler manifest operating in `Off` (Recommendation-only) mode with strict `minAllowed` and `maxAllowed` safety boundaries.
