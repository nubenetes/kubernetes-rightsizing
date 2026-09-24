# Chapter 4: From Metrics to a Safe Recommendation (VPA & KRR)

> **Reference:** Companion to Chapter 4 of *The Technical Guide to Kubernetes Rightsizing* ([LearnKube](https://learnkube.com/kubernetes-rightsizing)) and the Nubenetes video [Optimize K8s Resources](https://www.youtube.com/watch?v=aUIh_S8u5Z0).

---

| ⬅️ Previous | 🏠 Overview | Next ➡️ |
| :--- | :---: | ---: |
| [⬅️ Chapter 3: Telemetry & Metrics Pitfalls](03-metrics-telemetry-pitfalls.md) | [📚 Table of Contents](../README.md#table-of-contents) | [Chapter 5: Fleet-Scale Policy & GitOps ➡️](05-fleet-scale-policy-gitops.md) |

---

## 1. Comparing Recommendation Engines: KRR vs. VPA

Two major open-source tools dominate Kubernetes recommendation workflows: **Robusta KRR (Kubernetes Resource Recommender)** and the official **Kubernetes Vertical Pod Autoscaler (VPA)**.

| Feature | Robusta KRR | Kubernetes VPA |
| :--- | :--- | :--- |
| **Architecture** | CLI tool or scheduled batch job querying Prometheus | In-cluster control plane controllers (Recommender, Updater, Webhook) |
| **Calculation Model** | Direct PromQL statistical aggregations (percentiles & maxima) | Decaying weighted histograms with continuous decay factor |
| **CPU Strategy** | Default: $\text{p95}$ or $\text{p99}$ of CPU usage over lookback window | Target, LowerBound, and UpperBound derived from percentile distributions |
| **Memory Strategy** | Default: Maximum observed working set + safety buffer (e.g. 15%) | Maximum observed usage with exponential decay and OOM bump factor |
| **Execution Mode** | Informational reports (CLI, Slack, Markdown, YAML) | `Off` (Recommendation only), `Initial` (at pod creation), `Auto` (in-place eviction) |
| **Resource Impact** | Stateless; runs externally against Prometheus | Stateful; maintains memory checkpoints across cluster restarts |

---

## 2. Robusta KRR Mechanics

Robusta KRR operates by executing parameterized PromQL queries directly against Prometheus:

```mermaid
graph LR
    subgraph Inputs ["Data Inputs"]
        K8sAPI["Kubernetes API Server<br/>(Workload specs, current requests & limits)"]
        Prom[("Prometheus<br/>(Historical CPU/Memory metrics)")]
    end

    subgraph KRR ["Robusta KRR Engine"]
        Engine["Data Ingestion & Lookback Window<br/>(Default: 8d / configurable)"]
        Strategy{"Recommendation<br/>Strategy"}
        SimpleCalc["Simple Strategy (Default)<br/>• CPU: p95 + 5% buffer<br/>• Memory: Max + 15% buffer"]
        ConCalc["Conservative Strategy<br/>• CPU: p99 + 15% buffer<br/>• Memory: Max + 25% buffer"]
    end

    subgraph Outputs ["Reports"]
        Output["Output Formats<br/>(CLI / Table / YAML / JSON / Slack)"]
    end

    K8sAPI --> Engine
    Prom --> Engine
    Engine --> Strategy
    Strategy -->|Default Strategy| SimpleCalc
    Strategy -->|Conservative Strategy| ConCalc
    SimpleCalc --> Output
    ConCalc --> Output
```

### The Formula:

* **Recommended CPU Request:**
  $$\text{CPU}_{\text{rec}} = \max\left(\text{quantile}(0.95, \text{CPU Usage}[7\text{d}]), \text{Min CPU}\right) \times (1 + \text{buffer})$$
  *(Where $\text{CPU Usage}$ queries `container_cpu_usage` or `container_cpu_usage_seconds_total`)*
* **Recommended Memory Request:**
  $$\text{Mem}_{\text{rec}} = \max(\text{Working Set Memory}[7\text{d}]) \times (1 + \text{buffer})$$
  *(Where $\text{Working Set Memory}$ queries `container_memory_working_set`)*

---

## 3. Kubernetes Vertical Pod Autoscaler (VPA) Architecture

VPA splits its responsibilities across three decoupled controllers:

```mermaid
graph TD
    subgraph K8sControlPlane ["Kubernetes Control Plane"]
        APIServer["kube-apiserver"]
        ETCD[("etcd<br/>• VPA CRDs (Status & Target)<br/>• VPA Checkpoints")]
        APIServer <--> ETCD
    end

    subgraph VPAComponents ["VPA Architecture (3 Decoupled Components)"]
        Recommender["1. VPA Recommender<br/>(Decaying Histograms)"]
        Updater["2. VPA Updater<br/>(Eviction Engine)"]
        Admission["3. VPA Admission Controller<br/>(Mutating Webhook)"]
    end

    subgraph Telemetry ["Telemetry Sources"]
        Metrics[("Metrics Server / Prometheus")]
    end

    subgraph Workloads ["Cluster Workloads"]
        Deployment["Deployment / ReplicaSet Controller"]
        Pod["Target Pods"]
        Deployment -->|Manages| Pod
    end

    %% Recommender Flow
    Metrics -->|Real-time / Historical Usage| Recommender
    APIServer -->|Workload specs & VPA objects| Recommender
    Recommender -->|Writes recommendations & checkpoints| APIServer

    %% Updater Flow
    APIServer -->|Watches VPA targets & live pods| Updater
    Updater -->|Eviction API call| APIServer
    APIServer -.->|Evicts pod out of target range| Pod

    %% Admission Webhook Flow
    Deployment -->|Recreates replacement pod| APIServer
    APIServer -->|AdmissionReview request| Admission
    Admission -->|AdmissionResponse: Patched resource spec| APIServer
    APIServer -.->|Schedules rightsized pod| Pod
```

### VPA's Decaying Histogram Model
Unlike KRR, which queries raw metrics on demand, the VPA Recommender constructs internal **decaying histograms**:
* Histograms use exponentially growing buckets to represent CPU and memory values.
* Weights decay over time using a half-life factor (default: 24 hours), prioritizing recent behavior over historical behavior.
* **OOM Event Bump:** When a pod suffers an OOMKill, VPA immediately detects the event and artificially inflates the memory recommendation by a minimum factor (default: $+15\%$ to $+25\%$).

---

## 4. The Blind Spot of Both Models

Neither KRR nor VPA can infer application-level context:

1. **Scheduled Marketing Campaigns:** An engine observing a quiet Monday-through-Thursday has no awareness of a 10x traffic spike launching on Black Friday.
2. **Cold Initialization Spikes:** Neither model distinguishes between transient JVM classloading memory and genuine runtime request consumption.
3. **Autoscaler Conflicts (HPA vs. VPA):** If an HPA scales on CPU utilization percentage (e.g. 70%), lowering the CPU request concurrently increases the calculated utilization percentage, triggering unwanted HPA replica scale-outs!

---

## 5. Safe Operating Modes

* **Always start in `Off` / Recommendation-Only mode:** Never deploy VPA in `Auto` mode on production workloads without strict bounds.
* **Define `minAllowed` and `maxAllowed` constraints:**
  ```yaml
  resourcePolicy:
    containerPolicies:
      - containerName: app
        minAllowed:
          cpu: 250m
          memory: 512Mi
        maxAllowed:
          cpu: 4000m
          memory: 4Gi
  ```
* **Filter out ephemeral jobs:** Exclude batch jobs, CI/CD runners, and short-lived pods from fleet-wide analysis.

---

| ⬅️ Previous | 🏠 Overview | Next ➡️ |
| :--- | :---: | ---: |
| [⬅️ Chapter 3: Telemetry & Metrics Pitfalls](03-metrics-telemetry-pitfalls.md) | [📚 Table of Contents](../README.md#table-of-contents) | [Chapter 5: Fleet-Scale Policy & GitOps ➡️](05-fleet-scale-policy-gitops.md) |
