# AI Self-Hosted Blueprint (Codex-like Capabilities)

## 1. Target
Build a self-hosted AI stack with Codex-like behavior for:
- deep troubleshooting across infra/runtime;
- code editing, patching, testing, and review;
- real-time interventions with approvals, audit, and rollback.

Goal is not only a model file, but a deployable agent platform.

## 2. What You Must Ship (Bundle)
1. Model weights (open-weight)
2. Inference runtime (OpenAI-compatible API)
3. Agent orchestrator (planning + tool calling + retries)
4. Tool adapters (ssh, kubectl, git, ci, tests)
5. Policy engine (R0-R3 risk gating)
6. Knowledge/RAG layer (runbooks, incidents, architecture docs)
7. Observability + eval + audit

## 3. Recommended Runtime Choices

### 3.1 Primary (server GPU / production)
- Runtime: `vLLM`
- Why: high throughput, continuous batching, OpenAI-compatible endpoints, Kubernetes integration.
- API contract: `/v1/chat/completions`, `/v1/responses`, `/v1/models`.

### 3.2 Secondary (edge / on-prem small nodes)
- Runtime: `llama.cpp` or `Ollama`
- Why: lower footprint, simple local deployment, OpenAI-compatible style integration.

### 3.3 What to avoid for new greenfield
- `TGI` as primary engine for new builds, because docs state maintenance mode and recommend vLLM/SGLang/local engines.

## 4. Model Strategy (Self-hosted)

### 4.1 Baseline models
- `openai/gpt-oss-20b`
  - lower latency / 16GB-class deployments
  - good for local and specialized workloads
- `openai/gpt-oss-120b`
  - stronger reasoning and broader reliability
  - production profile on 80GB-class GPU

### 4.2 Important compatibility note
- gpt-oss model card requires Harmony format usage. Treat this as a hard requirement in your serving path and prompt adapter.

### 4.3 Portfolio option (recommended)
- Router policy:
  - default: `gpt-oss-20b`
  - escalate to `gpt-oss-120b` on hard tasks (multi-step debugging, large code reviews, incident coordination)

## 5. Deployment Profiles

### Profile A: Single-node edge/on-prem
- Runtime: Ollama or llama.cpp
- Model: gpt-oss-20b (or quantized fallback)
- Use cases: tenant-local assistants, private coding helper, fast low-cost troubleshooting
- Tradeoff: lower peak quality vs cluster-grade serving

### Profile B: Cluster production
- Runtime: vLLM on Kubernetes (direct or with KServe)
- Models: gpt-oss-20b + gpt-oss-120b
- Use cases: enterprise assistant, high concurrency, governed operations
- Tradeoff: higher ops complexity, GPU scheduling and cost management

## 6. Reference Architecture
```text
[Product API/UI]
    |
    v
[Agent Orchestrator]
    |-- planner
    |-- tool caller
    |-- approval manager
    |
    +--> [Model Gateway]
    |      |-- vLLM cluster endpoint
    |      |-- edge local endpoint (llama.cpp/Ollama)
    |
    +--> [Policy Engine R0-R3]
    +--> [RAG Store]
    +--> [Audit + Eval + Telemetry]
```

## 7. Security and Governance Baseline
- No R2/R3 action without approval (R3 dual approval).
- Mandatory rollback plan for R1+.
- Full audit log: command, operator/agent id, target env, result.
- Secret redaction in logs and responses.
- Per-environment tool allowlist and denylist.

## 8. Performance and Reliability SLOs (v1)
- P95 model latency (interactive):
  - edge profile: <= 4.0s first useful answer
  - cluster profile: <= 2.0s first useful answer
- Task success rate on eval suite: >= 85%
- Unsafe action rate (without required approval): 0%
- Evidence completeness in reports: >= 95%

## 9. Implementation Plan (Self-hosted First)

### Phase 1 (2 weeks)
- Deploy one runtime endpoint (`vLLM` or `Ollama`) with OpenAI-compatible API.
- Integrate orchestrator to existing policy files:
  - `docs/ai-agent-policy.yaml`
  - `docs/ai-agent-capability-matrix.md`
- Run first 10 eval scenarios.

### Phase 2 (3-4 weeks)
- Add model router (`20b` default, `120b` escalation).
- Add approval UI/API flow for R2/R3.
- Run full 20-case eval suite with regression tracking.

### Phase 3 (4-6 weeks)
- Hardening: multi-tenant isolation, autoscaling, DR plan.
- Add fine-tuning/LoRA lane for domain adaptation.
- Production SLO dashboard and incident playbooks.

## 10. Integration Contract for Product
- Required endpoints:
  - `POST /agent/sessions`
  - `POST /agent/sessions/{id}/messages`
  - `POST /agent/jobs`
  - `POST /agent/jobs/{id}/approve`
  - `GET /agent/jobs/{id}/events`
  - `GET /agent/jobs/{id}/report`
- Streaming strongly recommended for real-time operator UX.

## 11. Immediate Next Deliverables
1. `docs/ai-self-hosted-stack-selection.md` (choose primary runtime + hardware profile)
2. `docs/ai-self-hosted-runbook.md` (ops procedures: deploy, rollback, incident)
3. `docs/ai-self-hosted-benchmark.md` (latency/quality/cost benchmark template)

## 12. References (Primary Sources)
- OpenAI gpt-oss announcement:
  - https://openai.com/index/introducing-gpt-oss
- OpenAI gpt-oss model on Hugging Face (license, deployment notes, Harmony requirement):
  - https://huggingface.co/openai/gpt-oss-20b
- vLLM OpenAI-compatible serving:
  - https://docs.vllm.ai/en/latest/serving/openai_compatible_server/
- vLLM Kubernetes/KServe integration:
  - https://docs.vllm.ai/en/latest/deployment/integrations/kserve/
- KServe generative runtime overview:
  - https://kserve.github.io/website/docs/model-serving/generative-inference/overview
- llama.cpp (OpenAI-compatible server quick start):
  - https://github.com/ggml-org/llama.cpp
- Ollama docs + tool calling:
  - https://docs.ollama.com/
  - https://docs.ollama.com/capabilities/tool-calling
- Hugging Face TGI docs (maintenance mode note):
  - https://huggingface.co/docs/text-generation-inference/index
