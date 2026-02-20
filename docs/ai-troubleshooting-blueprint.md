# AI Troubleshooting Blueprint (Sysadmin + Coding)

## 1. Goal
Build an AI agent, embeddable in your product, able to:
- troubleshoot infrastructure and runtime issues;
- patch and validate code changes in real repositories;
- execute actions with safety controls, approvals, and audit trail.

## 2. Operating Principles
- Tool-first: actions must run through verifiable tools.
- Evidence-first: decisions must be backed by command/log outputs.
- Safe-by-default: risky actions require explicit approval.
- Git-first: code/config changes flow through branch, commit, PR.
- Rollback-ready: each mutation must have a rollback path.

## 3. Architecture
```text
[Product UI/API]
    |
    v
[Agent Orchestrator] -- [Policy Engine + Approval]
    |
    +-- [Model Gateway: primary/fallback]
    +-- [Tool Runtime: kubectl/helm/ssh/git/tests]
    +-- [Knowledge Layer: runbooks/docs/incidents]
    +-- [Telemetry + Eval + Audit]
```

## 4. Risk Model
- R0: read-only (status, logs, describe, diff)
- R1: reversible changes (restart, non-prod patch)
- R2: impactful changes (prod deploy/network changes) -> approval required
- R3: destructive changes (delete/purge/data loss) -> dual approval required

## 5. Standard Execution Loop
1. Intake (goal, env, urgency, impact)
2. Discovery (collect state + evidence)
3. Plan (minimal steps + risk level)
4. Execute (R0 first, then allowed mutations)
5. Verify (health checks/tests)
6. Report (what changed, evidence, rollback, next steps)

## 6. MVP Stack
- Orchestrator API: FastAPI or Node.js
- Workflow engine: Temporal
- State: PostgreSQL + Redis
- RAG: pgvector
- Secrets: Vault/cloud secrets manager
- Observability: OpenTelemetry + Prometheus + Grafana

## 7. First Deliverables
1. Capability matrix (tool x technology x risk)
2. Policy file (R0-R3 + approval rules)
3. Eval suite (at least 20 real troubleshooting cases)
