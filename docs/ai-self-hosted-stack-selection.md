# AI Self-Hosted Stack Selection

## 1. Scope
Select the runtime stack for a self-hosted, Codex-like agent platform.

Decision must optimize:
- quality on complex troubleshooting/coding tasks;
- predictable latency under concurrency;
- safe operations and easy rollback;
- portability across on-prem and cloud environments.

## 2. Final Recommendation

### Primary production path
- Inference runtime: `vLLM`
- Deployment: Kubernetes (direct deployment first, KServe optional in phase 2)
- Model policy:
  - default: `openai/gpt-oss-20b`
  - escalation: `openai/gpt-oss-120b` for hard tasks

### Secondary edge path
- Runtime: `Ollama` (or `llama.cpp` where footprint is critical)
- Model policy: `gpt-oss-20b` or quantized fallback

## 3. Why This Selection

### vLLM as primary
- High throughput and continuous batching.
- OpenAI-compatible API simplifies orchestrator integration.
- Good Kubernetes fit for autoscaling and governance.

### Ollama/llama.cpp as secondary
- Fast local setup.
- Good for private edge deployments and low-concurrency workloads.
- Easier tenant-local rollout where full GPU cluster is not available.

## 4. Non-Selected as Primary
- `TGI` is not selected as primary for greenfield due maintenance-mode positioning in official docs.

## 5. Hardware Profiles (Planning Baseline)

Use these as starting points, then tune with benchmark results.

### Profile S (edge/local)
- Target model: `gpt-oss-20b` quantized
- Concurrency target: 1-5 active sessions
- Best for: local assistants, low-latency private tasks

### Profile M (team service)
- Target model: `gpt-oss-20b` standard or mixed precision
- Concurrency target: 10-50 active sessions
- Best for: internal platform team operations

### Profile L (enterprise cluster)
- Target models: `gpt-oss-20b` + `gpt-oss-120b` routed
- Concurrency target: 50+ active sessions
- Best for: production agent in customer-facing product

## 6. Routing Policy (v1)
- Route to `20b` by default.
- Escalate to `120b` when one of these triggers is true:
  - multi-step incident diagnosis failed once on `20b`;
  - code review scope is large/high risk;
  - task classified `R2/R3` and requires deeper reasoning before approval.

## 7. Operational Constraints
- No `R2/R3` execution without policy approval gate.
- All `R1+` actions require rollback plan pre-execution.
- Mandatory audit evidence for every action.

## 8. Rollout Plan
1. Phase 1: deploy vLLM + `20b` only, integrate with existing policy/eval docs.
2. Phase 2: add `120b` endpoint + router + quality gates.
3. Phase 3: add edge runtime path and multi-tenant isolation.

## 9. Exit Criteria
- Latency and quality hit thresholds in benchmark doc.
- Unsafe action rate remains 0% for unapproved `R2/R3` operations.
- Full traceability for tool actions and approvals.
