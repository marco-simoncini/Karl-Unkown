from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


RiskLevel = Literal["R0", "R1", "R2", "R3"]
EnvironmentName = Literal["dev", "stage", "prod"]
JobStatus = Literal["queued", "running", "awaiting_approval", "done", "failed"]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SessionCreateRequest(BaseModel):
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SessionResponse(BaseModel):
    session_id: str
    created_at: str
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SessionMessageRequest(BaseModel):
    message: str = Field(min_length=1)
    environment: EnvironmentName = "dev"
    requested_risk: Optional[RiskLevel] = None


class SessionMessageResponse(BaseModel):
    session_id: str
    response: str
    risk_level: RiskLevel
    requires_approval: bool
    required_approvals: int
    timestamp_utc: str


class ToolResult(BaseModel):
    tool_name: str
    command: str
    exit_code: int
    stdout: str
    stderr: str
    started_at_utc: str
    finished_at_utc: str


class JobCreateRequest(BaseModel):
    goal: str = Field(min_length=1)
    environment: EnvironmentName = "dev"
    session_id: Optional[str] = None
    requested_risk: Optional[RiskLevel] = None
    run_diagnostics: bool = True


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    risk_level: RiskLevel
    required_approvals: int
    environment: EnvironmentName
    created_at: str
    updated_at: str


class JobApproveRequest(BaseModel):
    approver: str = Field(min_length=1)
    comment: Optional[str] = None


class JobEvent(BaseModel):
    timestamp_utc: str
    event_type: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


class JobReportResponse(BaseModel):
    job_id: str
    status: JobStatus
    risk_level: RiskLevel
    summary: str
    diagnostics: List[ToolResult] = Field(default_factory=list)
    approvals: List[Dict[str, Any]] = Field(default_factory=list)
    updated_at: str
