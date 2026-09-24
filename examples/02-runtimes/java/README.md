# Java JVM Kubernetes Sizing Lab

This directory demonstrates common JVM container configuration pitfalls versus production best practices.

## Pitfall (`deployment-bad.yaml`)
* Sets `-Xmx1024m` inside a container with a `1024Mi` memory limit.
* Fails to leave headroom for Metaspace, thread stacks, direct byte buffers, or JIT compilation.
* Result: Rapidly terminated by the Linux kernel with `OOMKilled` (Exit 137).

## Best Practice (`deployment-optimal.yaml`)
* Enables `-XX:+UseContainerSupport`.
* Sets `-XX:MaxRAMPercentage=75.0` to calculate heap size dynamically from the container limit.
* Leaves a 25% safety margin for off-heap allocations.
* Configures `-XX:+ExitOnOutOfMemoryError` to trigger clean pod restarts if heap space is exhausted.
