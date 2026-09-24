#!/usr/bin/env python3
"""
JVM Memory Sizing Calculator for Kubernetes Containers
Companion tool for: https://github.com/nubenetes/kubernetes-rightsizing
Reference: https://learnkube.com/kubernetes-rightsizing
"""
import argparse

def calculate_jvm_sizing(heap_mb: int, thread_count: int = 150, metaspace_mb: int = 128, direct_mb: int = 128):
    # Each thread stack defaults to 1MB under 64-bit Linux JVM
    stack_mb = thread_count * 1
    code_cache_mb = 64
    native_overhead_mb = 100

    non_heap_total = metaspace_mb + stack_mb + direct_mb + code_cache_mb + native_overhead_mb
    total_expected_mb = heap_mb + non_heap_total

    # Container limit should accommodate total expected memory + 15% safety buffer
    safe_container_limit_mb = int(total_expected_mb * 1.15)
    
    # Calculate MaxRAMPercentage
    max_ram_percentage = round((heap_mb / safe_container_limit_mb) * 100, 1)

    print("=" * 60)
    print("           JVM KUBERNETES CONTAINER SIZING REPORT           ")
    print("=" * 60)
    print(f"Target Heap (-Xmx):                 {heap_mb} MiB")
    print(f"Thread Stacks ({thread_count} threads @ 1MB):     {stack_mb} MiB")
    print(f"Estimated Metaspace:                {metaspace_mb} MiB")
    print(f"Direct Byte Buffers (NIO/Netty):    {direct_mb} MiB")
    print(f"JIT CodeCache + Native Overhead:    {code_cache_mb + native_overhead_mb} MiB")
    print("-" * 60)
    print(f"Total Non-Heap Overhead:            {non_heap_total} MiB")
    print(f"Total Estimated Working Set:        {total_expected_mb} MiB")
    print("=" * 60)
    print(f"RECOMMENDED CONTAINER MEMORY LIMIT: {safe_container_limit_mb} MiB")
    print(f"RECOMMENDED MaxRAMPercentage:       -XX:MaxRAMPercentage={max_ram_percentage}")
    print("=" * 60)
    print("\nRecommended Deployment Environment Flags:")
    print("  JAVA_TOOL_OPTIONS: >-")
    print("    -XX:+UseContainerSupport")
    print(f"    -XX:MaxRAMPercentage={max_ram_percentage}")
    print("    -XX:InitialRAMPercentage=50.0")
    print("    -XX:+ExitOnOutOfMemoryError")
    print("    -Djava.awt.headless=true")
    print("\nRecommended Container Resources:")
    print("  resources:")
    print(f"    requests:")
    print(f"      memory: \"{int(safe_container_limit_mb * 0.75)}Mi\"")
    print(f"    limits:")
    print(f"      memory: \"{safe_container_limit_mb}Mi\"")
    print("=" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate safe Kubernetes container limits for JVM applications.")
    parser.add_argument("--heap", type=int, default=1024, help="Target JVM heap in MiB (default: 1024)")
    parser.add_argument("--threads", type=int, default=150, help="Expected peak active thread count (default: 150)")
    parser.add_argument("--metaspace", type=int, default=128, help="Expected Metaspace usage in MiB (default: 128)")
    parser.add_argument("--direct", type=int, default=128, help="Expected Direct NIO buffer usage in MiB (default: 128)")
    
    args = parser.parse_args()
    calculate_jvm_sizing(args.heap, args.threads, args.metaspace, args.direct)
