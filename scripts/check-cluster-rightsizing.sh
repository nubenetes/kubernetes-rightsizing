#!/usr/bin/env bash
# ==============================================================================
# Kubernetes Cluster Rightsizing & Risk Audit
# Companion script for: https://github.com/nubenetes/kubernetes-rightsizing
# Reference: https://learnkube.com/kubernetes-rightsizing
# ==============================================================================
set -euo pipefail

echo "======================================================================"
echo "          NUBENETES KUBERNETES RIGHTSIZING AUDIT                     "
echo "======================================================================"

if ! command -v kubectl &>/dev/null; then
    echo "Error: kubectl is not installed or not in PATH."
    exit 1
fi

echo -e "\n[*] 1. Scanning for Pods recently terminated due to OOMKilled..."
kubectl get pods --all-namespaces -o jsonpath='{range .items[*]}{range .status.containerStatuses[*]}{.lastState.terminated.reason}{"\t"}{$.metadata.namespace}{"\t"}{$.metadata.name}{"\t"}{.name}{"\n"}{end}{end}' 2>/dev/null | grep -i "OOMKilled" || echo "  -> No OOMKilled containers detected in recent history."

echo -e "\n[*] 2. Checking for Containers without CPU or Memory Requests..."
kubectl get pods --all-namespaces -o json | python3 -c '
import sys, json
try:
    data = json.load(sys.stdin)
    missing = []
    for item in data.get("items", []):
        ns = item["metadata"]["namespace"]
        pod = item["metadata"]["name"]
        for c in item.get("spec", {}).get("containers", []):
            reqs = c.get("resources", {}).get("requests", {})
            if "cpu" not in reqs or "memory" not in reqs:
                missing.append((ns, pod, c["name"], "cpu" not in reqs, "memory" not in reqs))
    if missing:
        print(f"  Found {len(missing)} containers missing requests:")
        for ns, pod, cname, no_cpu, no_mem in missing[:10]:
            print(f"    - {ns}/{pod} ({cname}) [Missing: {\"CPU \" if no_cpu else \"\"}{\"Memory\" if no_mem else \"\"}]")
    else:
        print("  -> All evaluated containers specify requests.")
except Exception as e:
    print(f"  Audit check error: {e}")
'

echo -e "\n[*] 3. Identifying Containers with Tight CPU Limits (< 500m - High CFS Throttling Risk)..."
kubectl get pods --all-namespaces -o json | python3 -c '
import sys, json
try:
    data = json.load(sys.stdin)
    tight = []
    for item in data.get("items", []):
        ns = item["metadata"]["namespace"]
        pod = item["metadata"]["name"]
        for c in item.get("spec", {}).get("containers", []):
            limits = c.get("resources", {}).get("limits", {})
            cpu_lim = limits.get("cpu")
            if cpu_lim:
                # check if < 500m
                if cpu_lim.endswith("m") and int(cpu_lim[:-1]) <= 500:
                    tight.append((ns, pod, c["name"], cpu_lim))
    if tight:
        print(f"  Found {len(tight)} containers with CPU limit <= 500m:")
        for ns, pod, cname, lim in tight[:10]:
            print(f"    - {ns}/{pod} ({cname}) [Limit: {lim}]")
    else:
        print("  -> No containers found with tight CPU limits <= 500m.")
except Exception as e:
    print(f"  Audit check error: {e}")
'

echo -e "\n======================================================================"
echo "Audit complete! For deep remediation, see: https://learnkube.com/kubernetes-rightsizing"
echo "======================================================================"
