# Autonomous Rightsizing Agent Workflow

```mermaid
stateDiagram-v2
    [*] --> IngestMetrics: Query Prometheus (14-day Window)
    IngestMetrics --> CalculateCandidate: Apply Statistical Model (p99 CPU, Max RAM)
    CalculateCandidate --> SelectionPolicy: Is Monthly Delta > $50 OR CPU Delta > 35%?
    
    SelectionPolicy --> Skip: No (Noise reduction)
    Skip --> [*]

    SelectionPolicy --> StaleCheck: Yes (Candidate accepted)
    StaleCheck --> Invalidate: Git commit timestamp > Metric window start
    Invalidate --> [*]: Abort (Evidence stale due to recent code changes)
    
    StaleCheck --> GeneratePR: Verification passed
    GeneratePR --> HumanReview: Submit GitOps PR with Evidence Record
    HumanReview --> CanaryRollout: Approved & Merged
    
    CanaryRollout --> MonitorCanary: Evaluate Error Rate & Restarts (30m)
    MonitorCanary --> RollbackTriggered: 5xx > 0.1% OR Restarts > 0
    RollbackTriggered --> AutoRevert: Automated Git Revert PR
    MonitorCanary --> Healthy: Baseline confirmed healthy
    AutoRevert --> [*]
    Healthy --> [*]
```

## Agent Invariants & Guardrails
1. **Never patch live cluster resources directly:** The agent must only interact via Git Pull Requests.
2. **Never overwrite manual engineer overrides:** Respect `@rightsizing: ignore` annotations.
3. **Always attach evidence provenance:** Every PR must cite the query, lookback window, and reference guide.
