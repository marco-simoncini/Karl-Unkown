from __future__ import annotations

from typing import Any, Dict, Optional

from agent.config import Settings
from agent.llm import OllamaClient
from agent.models import (
    EnvironmentName,
    JobApproveRequest,
    JobCreateRequest,
    JobReportResponse,
    JobResponse,
    RiskLevel,
    SessionMessageRequest,
    SessionMessageResponse,
    utc_now_iso,
)
from agent.policy import PolicyEngine
from agent.store import InMemoryStore
from agent.tools import run_read_only_diagnostics


class AgentOrchestrator:
    def __init__(
        self,
        settings: Settings,
        policy: PolicyEngine,
        store: InMemoryStore,
        llm: OllamaClient,
    ) -> None:
        self.settings = settings
        self.policy = policy
        self.store = store
        self.llm = llm

    def classify_risk(self, text: str, explicit_risk: Optional[RiskLevel] = None) -> RiskLevel:
        if explicit_risk:
            return explicit_risk

        lowered = text.lower()
        r3_keywords = ("wipe", "purge", "delete all", "drop database", "destroy", "format disk")
        r2_keywords = ("prod deploy", "production deploy", "ingress change", "schema migration")
        r1_keywords = ("restart", "scale", "patch", "update dependency", "upgrade")

        if any(keyword in lowered for keyword in r3_keywords):
            return "R3"
        if any(keyword in lowered for keyword in r2_keywords):
            return "R2"
        if any(keyword in lowered for keyword in r1_keywords):
            return "R1"
        return "R0"

    async def handle_message(
        self, session_id: str, request: SessionMessageRequest
    ) -> SessionMessageResponse:
        session = self.store.get_session(session_id)
        if not session:
            raise KeyError(f"Session not found: {session_id}")

        risk_level = self.classify_risk(request.message, request.requested_risk)
        required_approvals = self.policy.required_approvals(risk_level, request.environment)
        requires_approval = required_approvals > 0

        self.store.append_session_message(session_id, "user", request.message)
        if requires_approval:
            response = (
                f"Request classified as {risk_level} in {request.environment}. "
                f"This requires {required_approvals} approval(s). "
                "Create a job via POST /agent/jobs to continue."
            )
        else:
            system_prompt = (
                "You are a pragmatic SRE/coding assistant. Provide concise, evidence-driven "
                "next steps and mention rollback considerations when relevant."
            )
            response = await self.llm.chat(system_prompt, request.message)

        self.store.append_session_message(session_id, "assistant", response)
        return SessionMessageResponse(
            session_id=session_id,
            response=response,
            risk_level=risk_level,
            requires_approval=requires_approval,
            required_approvals=required_approvals,
            timestamp_utc=utc_now_iso(),
        )

    async def create_job(self, request: JobCreateRequest) -> JobResponse:
        risk_level = self.classify_risk(request.goal, request.requested_risk)
        required_approvals = self.policy.required_approvals(risk_level, request.environment)
        status = "awaiting_approval" if required_approvals > 0 else "queued"

        job = self.store.create_job(
            {
                "status": status,
                "risk_level": risk_level,
                "environment": request.environment,
                "goal": request.goal,
                "session_id": request.session_id,
                "required_approvals": required_approvals,
                "run_diagnostics": request.run_diagnostics,
            }
        )
        self.store.add_job_event(
            job["job_id"],
            "job_created",
            "Job created",
            {
                "risk_level": risk_level,
                "required_approvals": required_approvals,
                "environment": request.environment,
            },
        )

        if status != "awaiting_approval":
            await self._execute_job(job["job_id"])
            job = self.store.get_job(job["job_id"]) or job

        return self._to_job_response(job)

    async def approve_job(self, job_id: str, request: JobApproveRequest) -> JobResponse:
        job = self.store.get_job(job_id)
        if not job:
            raise KeyError(f"Job not found: {job_id}")

        job = self.store.add_job_approval(job_id, request.approver, request.comment)
        self.store.add_job_event(
            job_id,
            "job_approved",
            "Approval registered",
            {"approver": request.approver, "comment": request.comment or ""},
        )

        if (
            job["status"] == "awaiting_approval"
            and len(job["approvals"]) >= job["required_approvals"]
        ):
            await self._execute_job(job_id)
            job = self.store.get_job(job_id) or job

        return self._to_job_response(job)

    async def _execute_job(self, job_id: str) -> None:
        job = self.store.set_job_status(job_id, "running")
        self.store.add_job_event(job_id, "job_started", "Job execution started")

        diagnostics = []
        try:
            if job.get("run_diagnostics", True):
                diagnostics = await run_read_only_diagnostics(
                    repo_root=self.settings.repo_root,
                    timeout=self.settings.command_timeout_seconds,
                )
                self.store.add_job_event(
                    job_id,
                    "diagnostics_completed",
                    "Read-only diagnostics completed",
                    {"checks": len(diagnostics)},
                )

            summary_prompt = self._build_summary_prompt(job["goal"], diagnostics)
            summary = await self.llm.chat(
                "You summarize diagnostics for SRE and coding teams with concise action items.",
                summary_prompt,
            )

            report = {
                "job_id": job_id,
                "status": "done",
                "risk_level": job["risk_level"],
                "summary": summary,
                "diagnostics": [result.model_dump() for result in diagnostics],
                "approvals": job.get("approvals", []),
                "updated_at": utc_now_iso(),
            }
            self.store.set_job_report(job_id, report)
            self.store.set_job_status(job_id, "done")
            self.store.add_job_event(job_id, "job_done", "Job completed successfully")
        except Exception as exc:  # noqa: BLE001
            report = {
                "job_id": job_id,
                "status": "failed",
                "risk_level": job["risk_level"],
                "summary": f"Execution failed: {exc}",
                "diagnostics": [result.model_dump() for result in diagnostics],
                "approvals": job.get("approvals", []),
                "updated_at": utc_now_iso(),
            }
            self.store.set_job_report(job_id, report)
            self.store.set_job_status(job_id, "failed")
            self.store.add_job_event(
                job_id, "job_failed", "Job failed", {"error": str(exc)}
            )

    @staticmethod
    def _build_summary_prompt(goal: str, diagnostics: list[Any]) -> str:
        lines = [f"Goal: {goal}", "", "Diagnostics:"]
        for item in diagnostics:
            stdout_excerpt = (item.stdout or "").strip().splitlines()[:6]
            stderr_excerpt = (item.stderr or "").strip().splitlines()[:6]
            lines.append(f"- {item.tool_name} | exit={item.exit_code}")
            if stdout_excerpt:
                lines.append("  stdout:")
                lines.extend(f"    {line}" for line in stdout_excerpt)
            if stderr_excerpt:
                lines.append("  stderr:")
                lines.extend(f"    {line}" for line in stderr_excerpt)
        lines.append("")
        lines.append("Provide: likely root cause, safe next actions, and rollback notes.")
        return "\n".join(lines)

    def _to_job_response(self, job: Dict[str, Any]) -> JobResponse:
        return JobResponse(
            job_id=job["job_id"],
            status=job["status"],
            risk_level=job["risk_level"],
            required_approvals=job["required_approvals"],
            environment=job["environment"],
            created_at=job["created_at"],
            updated_at=job["updated_at"],
        )

    def get_job_report(self, job_id: str) -> JobReportResponse:
        job = self.store.get_job(job_id)
        if not job:
            raise KeyError(f"Job not found: {job_id}")
        report = job.get("report")
        if not report:
            report = {
                "job_id": job_id,
                "status": job["status"],
                "risk_level": job["risk_level"],
                "summary": "Job report is not available yet.",
                "diagnostics": [],
                "approvals": job.get("approvals", []),
                "updated_at": job["updated_at"],
            }
        return JobReportResponse(**report)

    def get_job_events(self, job_id: str) -> list[Dict[str, Any]]:
        job = self.store.get_job(job_id)
        if not job:
            raise KeyError(f"Job not found: {job_id}")
        return self.store.get_job_events(job_id)
