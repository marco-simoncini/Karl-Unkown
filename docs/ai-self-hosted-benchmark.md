# AI Self-Hosted Benchmark Template

## 1. Objective
Measure quality, latency, reliability, and cost before production rollout.

## 2. Test Scope

### 2.1 Quality
- Use `docs/ai-agent-eval-suite.md` as baseline.
- Minimum set:
  - 10 infra scenarios
  - 10 coding scenarios

### 2.2 Performance
- Measure:
  - time to first useful token
  - full response latency
  - throughput under concurrency
- Load profiles:
  - C1: 1 user
  - C2: 10 users
  - C3: 50 users

### 2.3 Reliability
- Runtime crash rate
- timeout rate
- tool-call failure rate

### 2.4 Cost
- Compute cost per 1k requests
- Average cost per resolved task

## 3. Benchmark Matrix
| Runtime | Model | Environment | Concurrency | Avg Prompt Size | Avg Output Size | Notes |
|---|---|---|---:|---:|---:|---|
| vLLM | gpt-oss-20b | stage | 1 | | | |
| vLLM | gpt-oss-20b | stage | 10 | | | |
| vLLM | gpt-oss-20b | stage | 50 | | | |
| vLLM | gpt-oss-120b | stage | 1 | | | |
| vLLM | gpt-oss-120b | stage | 10 | | | |
| Ollama/llama.cpp | gpt-oss-20b (quantized) | edge | 1 | | | |

## 4. Result Template

### 4.1 Quality Results
| Suite | Pass | Partial | Fail | Pass Rate |
|---|---:|---:|---:|---:|
| Infra (10) | | | | |
| Coding (10) | | | | |
| Total (20) | | | | |

### 4.2 Performance Results
| Runtime | Model | Concurrency | P50 Latency (s) | P95 Latency (s) | Tokens/s | Timeout Rate |
|---|---|---:|---:|---:|---:|---:|
| | | | | | | |

### 4.3 Reliability Results
| Metric | Value | Threshold | Pass/Fail |
|---|---:|---:|---|
| Runtime crash rate | | | |
| Tool-call failure rate | | | |
| Unsafe action rate | | 0 | |

### 4.4 Cost Results
| Runtime | Model | Cost / 1k requests | Cost / resolved task | Notes |
|---|---|---:|---:|---|
| | | | | |

## 5. Acceptance Gates (v1)
- Overall eval pass rate: `>= 85%`
- Unsafe action rate for unapproved `R2/R3`: `0%`
- Evidence completeness: `>= 95%`
- P95 latency target:
  - edge profile: `<= 4.0s` first useful answer
  - cluster profile: `<= 2.0s` first useful answer

## 6. Decision Output
At the end of each benchmark cycle, produce:
1. go/no-go decision;
2. top 3 blockers;
3. remediation plan and retest date.
