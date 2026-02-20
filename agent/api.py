from __future__ import annotations

import os
from fastapi import FastAPI, HTTPException

from agent.config import get_settings
from agent.llm import OllamaClient
from agent.models import (
    JobApproveRequest,
    JobCreateRequest,
    JobEvent,
    JobReportResponse,
    JobResponse,
    SessionCreateRequest,
    SessionMessageRequest,
    SessionMessageResponse,
    SessionResponse,
)
from agent.orchestrator import AgentOrchestrator
from agent.policy import PolicyEngine
from agent.store import InMemoryStore


settings = get_settings()
policy_engine = PolicyEngine.from_file(settings.policy_path)
store = InMemoryStore()
llm = OllamaClient(
    base_url=settings.ollama_base_url,
    model=settings.ollama_model,
    timeout_seconds=settings.ollama_timeout_seconds,
    api_key=os.getenv("OLLAMA_API_KEY"),
)
orchestrator = AgentOrchestrator(
    settings=settings,
    policy=policy_engine,
    store=store,
    llm=llm,
)

app = FastAPI(title=settings.app_name, version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/agent/sessions", response_model=SessionResponse)
async def create_session(request: SessionCreateRequest) -> SessionResponse:
    session = store.create_session(request.user_id, request.metadata)
    return SessionResponse(**session)


@app.post("/agent/sessions/{session_id}/messages", response_model=SessionMessageResponse)
async def send_message(session_id: str, request: SessionMessageRequest) -> SessionMessageResponse:
    try:
        return await orchestrator.handle_message(session_id, request)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/agent/jobs", response_model=JobResponse)
async def create_job(request: JobCreateRequest) -> JobResponse:
    try:
        return await orchestrator.create_job(request)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/agent/jobs/{job_id}/approve", response_model=JobResponse)
async def approve_job(job_id: str, request: JobApproveRequest) -> JobResponse:
    try:
        return await orchestrator.approve_job(job_id, request)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/agent/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str) -> JobResponse:
    job = store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    return JobResponse(
        job_id=job["job_id"],
        status=job["status"],
        risk_level=job["risk_level"],
        required_approvals=job["required_approvals"],
        environment=job["environment"],
        created_at=job["created_at"],
        updated_at=job["updated_at"],
    )


@app.get("/agent/jobs/{job_id}/events", response_model=list[JobEvent])
async def get_job_events(job_id: str) -> list[JobEvent]:
    try:
        events = orchestrator.get_job_events(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return [JobEvent(**event) for event in events]


@app.get("/agent/jobs/{job_id}/report", response_model=JobReportResponse)
async def get_job_report(job_id: str) -> JobReportResponse:
    try:
        return orchestrator.get_job_report(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
