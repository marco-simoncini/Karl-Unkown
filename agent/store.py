from __future__ import annotations

from copy import deepcopy
from threading import Lock
from typing import Any, Dict, List, Optional
from uuid import uuid4

from agent.models import JobStatus, utc_now_iso


class InMemoryStore:
    def __init__(self) -> None:
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._jobs: Dict[str, Dict[str, Any]] = {}
        self._job_events: Dict[str, List[Dict[str, Any]]] = {}
        self._lock = Lock()

    def create_session(self, user_id: Optional[str], metadata: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            session_id = str(uuid4())
            session = {
                "session_id": session_id,
                "created_at": utc_now_iso(),
                "user_id": user_id,
                "metadata": metadata,
                "messages": [],
            }
            self._sessions[session_id] = session
            return deepcopy(session)

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            session = self._sessions.get(session_id)
            return deepcopy(session) if session else None

    def append_session_message(
        self,
        session_id: str,
        role: str,
        content: str,
    ) -> None:
        with self._lock:
            session = self._sessions[session_id]
            session["messages"].append(
                {"role": role, "content": content, "timestamp_utc": utc_now_iso()}
            )

    def create_job(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            job_id = str(uuid4())
            now = utc_now_iso()
            job = {
                "job_id": job_id,
                "status": payload["status"],
                "risk_level": payload["risk_level"],
                "environment": payload["environment"],
                "goal": payload["goal"],
                "session_id": payload.get("session_id"),
                "required_approvals": payload["required_approvals"],
                "run_diagnostics": payload.get("run_diagnostics", True),
                "approvals": [],
                "created_at": now,
                "updated_at": now,
                "report": None,
            }
            self._jobs[job_id] = job
            self._job_events[job_id] = []
            return deepcopy(job)

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            job = self._jobs.get(job_id)
            return deepcopy(job) if job else None

    def set_job_status(self, job_id: str, status: JobStatus) -> Dict[str, Any]:
        with self._lock:
            job = self._jobs[job_id]
            job["status"] = status
            job["updated_at"] = utc_now_iso()
            return deepcopy(job)

    def set_job_report(self, job_id: str, report: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            job = self._jobs[job_id]
            job["report"] = report
            job["updated_at"] = utc_now_iso()
            return deepcopy(job)

    def add_job_approval(
        self, job_id: str, approver: str, comment: Optional[str]
    ) -> Dict[str, Any]:
        with self._lock:
            job = self._jobs[job_id]
            job["approvals"].append(
                {
                    "approver": approver,
                    "comment": comment,
                    "timestamp_utc": utc_now_iso(),
                }
            )
            job["updated_at"] = utc_now_iso()
            return deepcopy(job)

    def add_job_event(
        self, job_id: str, event_type: str, message: str, details: Optional[Dict[str, Any]] = None
    ) -> None:
        with self._lock:
            self._job_events[job_id].append(
                {
                    "timestamp_utc": utc_now_iso(),
                    "event_type": event_type,
                    "message": message,
                    "details": details or {},
                }
            )

    def get_job_events(self, job_id: str) -> List[Dict[str, Any]]:
        with self._lock:
            return deepcopy(self._job_events.get(job_id, []))
