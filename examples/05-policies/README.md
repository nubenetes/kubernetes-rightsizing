# Policy & Governance Lab (Kyverno)

Demonstrates how platform teams codify rightsizing standards across clusters using Kyverno admission policies.

## Included Policies:
1. `kyverno-require-requests.yaml`: Enforces that all containers define both CPU and memory requests to prevent unconstrained cluster scheduling.
2. `kyverno-disallow-cpu-limits.yaml`: Disallows setting CPU limits on latency-sensitive tiers to eliminate Linux CFS throttling.
3. `kyverno-guaranteed-qos.yaml`: Enforces that tier-1 mission-critical pods configure identical requests and limits (`requests == limits`) to secure Kubernetes Guaranteed QoS status.
