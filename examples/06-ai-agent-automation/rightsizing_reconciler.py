#!/usr/bin/env bash
""":"
exec python3 "$0" "$@"
"""
import sys
import json
import dataclasses
from typing import Optional, Dict

@dataclasses.dataclass
class WorkloadEvidence:
    namespace: str
    workload: str
    container: str
    git_repo: str
    last_commit_timestamp: int
    metric_window_start_timestamp: int
    current_cpu_request_m: int
    current_mem_request_mib: int
    observed_p99_cpu_m: int
    observed_max_mem_mib: int

class RightsizingReconciler:
    def __init__(self, min_cpu_delta_pct: float = 30.0, min_mem_delta_pct: float = 25.0):
        self.min_cpu_delta_pct = min_cpu_delta_pct
        self.min_mem_delta_pct = min_mem_delta_pct

    def evaluate_workload(self, evidence: WorkloadEvidence) -> Optional[Dict]:
        print(f"[*] Evaluating {evidence.namespace}/{evidence.workload}:{evidence.container}...")

        # 1. Stale-Change Check
        if evidence.last_commit_timestamp > evidence.metric_window_start_timestamp:
            print(f"    [!] ABORT: Stale revision detected. Git commit happened after metric collection began.")
            return None

        # 2. Calculation Model (15% CPU safety buffer, 25% Memory safety buffer)
        recommended_cpu_m = max(50, int(evidence.observed_p99_cpu_m * 1.15))
        recommended_mem_mib = max(128, int(evidence.observed_max_mem_mib * 1.25))

        # 3. Selection Policy (Noise reduction filter)
        cpu_delta_pct = abs(evidence.current_cpu_request_m - recommended_cpu_m) / evidence.current_cpu_request_m * 100
        mem_delta_pct = abs(evidence.current_mem_request_mib - recommended_mem_mib) / evidence.current_mem_request_mib * 100

        if cpu_delta_pct < self.min_cpu_delta_pct and mem_delta_pct < self.min_mem_delta_pct:
            print(f"    [-] IGNORE: Delta too small (CPU: {cpu_delta_pct:.1f}%, Mem: {mem_delta_pct:.1f}%). Below selection threshold.")
            return None

        print(f"    [+] ACCEPTED: Material rightsizing opportunity found.")
        print(f"        CPU: {evidence.current_cpu_request_m}m -> {recommended_cpu_m}m (-{cpu_delta_pct:.1f}%)")
        print(f"        Memory: {evidence.current_mem_request_mib}Mi -> {recommended_mem_mib}Mi (-{mem_delta_pct:.1f}%)")

        return {
            "target": f"{evidence.namespace}/{evidence.workload}",
            "container": evidence.container,
            "patch": {
                "resources": {
                    "requests": {
                        "cpu": f"{recommended_cpu_m}m",
                        "memory": f"{recommended_mem_mib}Mi"
                    }
                }
            },
            "provenance": {
                "reference": "https://learnkube.com/kubernetes-rightsizing",
                "observed_p99_cpu": f"{evidence.observed_p99_cpu_m}m",
                "observed_max_memory": f"{evidence.observed_max_mem_mib}Mi"
            }
        }

if __name__ == "__main__":
    reconciler = RightsizingReconciler()

    # Sample workload telemetry payload
    sample_evidence = WorkloadEvidence(
        namespace="production",
        workload="payment-gateway",
        container="api",
        git_repo="git@github.com:nubenetes/payment-gateway.git",
        last_commit_timestamp=1710000000,
        metric_window_start_timestamp=1710100000,
        current_cpu_request_m=2000,
        current_mem_request_mib=4096,
        observed_p99_cpu_m=450,
        observed_max_mem_mib=1200
    )

    action = reconciler.evaluate_workload(sample_evidence)
    if action:
        print("\nGenerated GitOps Pull Request Patch:")
        print(json.dumps(action, indent=2))
