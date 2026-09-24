# AI Agent Automation & GitOps Lab

Demonstrates how to build a safe, deterministic, autonomous rightsizing pipeline where an AI/reconciler agent analyzes telemetry, inspects Git provenance, checks for stale changes, and submits a pull request with full evidence provenance.

## Included Components:
1. `agent-workflow.md`: Complete autonomous decision tree and guardrail architecture.
2. `rightsizing_reconciler.py`: Executable Python script implementing evidence gathering, policy filtering, stale revision validation, and declarative patch calculation.
3. `github-action-pr-verification.yaml`: CI pipeline verifying incoming rightsizing pull requests against production rollback conditions.
