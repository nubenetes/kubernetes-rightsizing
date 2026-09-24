# Go (Golang) Kubernetes Sizing Lab

Demonstrates configuring `GOMEMLIMIT` (Go 1.19+) and container-aware `GOMAXPROCS` using `go.uber.org/automaxprocs`.

## Key Concepts
1. **`GOMEMLIMIT`:** Soft target that guides the Go garbage collector to run aggressively before breaching the Linux cgroup limit.
2. **`automaxprocs`:** Prevents Go from creating thread pools sized to the physical host cores, eliminating CFS quota contention.
