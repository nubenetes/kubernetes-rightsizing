# Runtime Guide: Java & the JVM in Kubernetes

> **Reference:** Companion to Appendix A of *The Technical Guide to Kubernetes Rightsizing* ([LearnKube](https://learnkube.com/kubernetes-rightsizing)) and the Nubenetes Short [Why Java Containers Crash in Kubernetes](https://www.youtube.com/shorts/TALoXBzoP18).

---

## 1. Why Java Containers Crash (The Memory Anatomy)

Setting container memory limits equal to the JVM maximum heap (`-Xmx`) is the single most common cause of `OOMKilled` containers in Kubernetes.

```mermaid
graph TD
    subgraph Container Memory Limit e.g. 2048MiB
        subgraph JVM Process Total Memory MaxRAM
            Heap["JVM Heap (-Xmx / MaxRAMPercentage)<br/>Young & Old Generations<br/>(e.g., 70% = 1433MiB)"]
            subgraph Non-Heap Off-Heap Allocations ~30%
                Metaspace["Metaspace<br/>(Classes & Methods)"]
                Stacks["Thread Stacks<br/>(1MB per thread * 150 threads)"]
                CodeCache["JIT Code Cache<br/>(Compiled native code)"]
                DirectBuffers["Direct Byte Buffers<br/>(Netty / NIO Network I/O)"]
                NativeLibs["Native Libraries<br/>(glibc, OpenSSL, snappy)"]
                GCOverhead["GC Internal Data Structures"]
            end
        end
    end
```

$$\text{Total JVM Memory} = \text{Heap} + \text{Metaspace} + (\text{Thread Count} \times \text{Stack Size}) + \text{Direct Buffers} + \text{CodeCache} + \text{Native Overhead}$$

If a Java process uses 1.4GB of heap in a 2GB container, but spawns 250 threads (250MB stacks), loads 150MB of Netty network buffers, and uses 120MB Metaspace, total memory reaches $1920\text{MB}$. A minor burst immediately trips the Linux `cgroup` boundary, triggering an instant `SIGKILL` (exit code 137).

---

## 2. Best Practice JVM Container Flags

Since Java 10+ (and Java 8u191+), the HotSpot JVM supports container cgroups natively via `-XX:+UseContainerSupport` (enabled by default).

### Recommended Production Flags:
```bash
java \
  -XX:+UseContainerSupport \
  -XX:MaxRAMPercentage=75.0 \
  -XX:InitialRAMPercentage=50.0 \
  -XX:+ExitOnOutOfMemoryError \
  -XX:+HeapDumpOnOutOfMemoryError \
  -XX:HeapDumpPath=/tmp/heapdump.hprof \
  -Djava.awt.headless=true \
  -jar app.jar
```

### Key Explanations:
* `-XX:MaxRAMPercentage=75.0`: Dynamically assigns up to 75% of the container's `resources.limits.memory` to the heap, reserving a safe 25% buffer for thread stacks, Metaspace, and native allocators.
* `-XX:+ExitOnOutOfMemoryError`: Forces the JVM to terminate if internal heap space is exhausted, generating a clear exit code and triggering Kubernetes pod restart before the kernel abruptly kills the process without diagnostics.

---

## 3. CPU Sizing & JVM Active Processor Count

By default, the JVM determines its internal thread pool sizing (common `ForkJoinPool`, parallel GC threads, and JIT compilation threads) using the detected CPU count:
* If no CPU limit is set, the JVM queries the host node and may spin up 32 to 64 GC threads on a massive Kubernetes node, causing excessive context switching and memory consumption.
* If a CPU limit is set (e.g. `500m`), the JVM detects `< 1` core and may scale down to a single GC thread, leading to long GC pause times.

### Override for Thread Pools:
```bash
-XX:ActiveProcessorCount=2
```
Manually align JVM concurrency to match your expected workload throughput rather than node or fractional limit defaults.
