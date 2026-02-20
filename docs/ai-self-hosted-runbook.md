# AI Self-Hosted Runbook

## 1. Purpose
Operational procedures for deployment, rollback, and incident handling of the self-hosted AI stack.

## 2. Components
- Inference runtime (`vLLM` primary, `Ollama/llama.cpp` optional edge)
- Agent orchestrator
- Policy engine
- RAG store
- Audit/telemetry pipeline

## 3. Prerequisites
- Kubernetes access and namespace isolation
- Secret management available (Vault or cloud secret manager)
- Object/storage path for model artifacts
- Metrics and logs pipeline enabled

## 4. Standard Operations

### 4.1 Deploy new runtime version
1. Validate config in non-prod.
2. Run dry-run if supported.
3. Deploy canary replica.
4. Verify health and model readiness.
5. Shift traffic gradually.
6. Close change with evidence.

### 4.2 Deploy new model version
1. Register model artifact and checksum.
2. Warm model instance.
3. Run smoke prompts + eval subset.
4. Enable traffic slice (5% -> 25% -> 100%).
5. Monitor latency/error/quality signals.

### 4.3 Rollback
1. Trigger rollback if SLO breach or severe quality regression.
2. Re-route to last known good model/runtime.
3. Re-run smoke checks.
4. Annotate incident timeline and root cause ticket.

## 5. Health Checks

### 5.1 Runtime health
- API liveness endpoint reachable.
- Model list endpoint returns expected model IDs.
- Inference request returns valid completion.

### 5.2 Agent health
- Tool calling works (`git`, `kubectl`, `tests`) in read-only mode.
- Policy gating enforces approval for `R2/R3`.
- Audit pipeline stores action records.

## 6. Incident Response Playbooks

### INC-01 Latency spike
- Symptoms: p95 latency above threshold.
- Checks:
  - runtime queue depth
  - GPU/CPU saturation
  - token length outliers
- Actions:
  - reduce max concurrency
  - route heavy tasks to larger model pool
  - scale runtime replicas

### INC-02 OOM or runtime crashes
- Symptoms: pod restarts, failed inference.
- Checks:
  - memory usage trend
  - model load parameters
  - recent deployment changes
- Actions:
  - rollback to previous runtime config
  - lower batch size/context size
  - isolate heavy workloads

### INC-03 Quality regression
- Symptoms: wrong diagnoses, poor code patches.
- Checks:
  - compare pass rate vs eval baseline
  - inspect routing decisions
  - inspect prompt/policy changes
- Actions:
  - route critical tasks to stronger model
  - rollback prompt or model version
  - run full eval suite before re-enable

### INC-04 Approval/policy bypass attempt
- Symptoms: attempt to execute `R2/R3` without approval.
- Actions:
  - block execution
  - alert security/platform owners
  - keep immutable audit record

## 7. Change Management
- All production changes require change ID/ticket.
- All `R2/R3` actions require explicit approvals.
- Post-change report must include rollback status and evidence.

## 8. Backup and DR
- Backup policy/eval docs and model router config.
- Keep last known good runtime+model deployment artifacts.
- Test restore at least monthly.

## 9. On-call Checklist
- Check service status, latency, error rate, quality alarms.
- Verify approval queue health.
- Verify audit ingestion.
- Verify rollback path readiness.
