# Karl-Unkown

## AI Blueprint
Blueprint for a production-ready troubleshooting agent (sysadmin + coding):

- `docs/ai-troubleshooting-blueprint.md`
- `docs/ai-self-hosted-blueprint.md`
- `docs/ai-self-hosted-stack-selection.md`
- `docs/ai-self-hosted-runbook.md`
- `docs/ai-self-hosted-benchmark.md`
- `docs/ai-agent-capability-matrix.md`
- `docs/ai-agent-policy.yaml`
- `docs/ai-agent-eval-suite.md`

## MVP API (Ollama)
Minimal self-hosted scaffold is included in this repository:

- `main.py`
- `agent/` package (API, orchestrator, policy engine, tool runtime)
- `requirements.txt`

### Prerequisites
1. Python 3.10+
2. Ollama running locally (or any OpenAI-compatible endpoint)
3. Policy file available at `docs/ai-agent-policy.yaml`

### Install
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configure
Environment variables (optional):

- `OLLAMA_BASE_URL` default: `http://localhost:11434/v1`
- `OLLAMA_MODEL` default: `gpt-oss:20b`
- `OLLAMA_TIMEOUT_SECONDS` default: `60`
- `AGENT_POLICY_PATH` default: `docs/ai-agent-policy.yaml`
- `AGENT_REPO_ROOT` default: current working directory
- `AGENT_COMMAND_TIMEOUT_SECONDS` default: `30`

### Run
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### API Endpoints
- `GET /health`
- `POST /agent/sessions`
- `POST /agent/sessions/{id}/messages`
- `POST /agent/jobs`
- `POST /agent/jobs/{id}/approve`
- `GET /agent/jobs/{id}`
- `GET /agent/jobs/{id}/events`
- `GET /agent/jobs/{id}/report`

### Quick smoke test
```bash
curl -s -X POST http://localhost:8000/agent/sessions \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"demo"}'
```
