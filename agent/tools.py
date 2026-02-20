from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Sequence

from agent.models import ToolResult


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def _run_command(command: Sequence[str], cwd: Path, tool_name: str, timeout: int) -> ToolResult:
    started_at = _now_iso()
    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            cwd=str(cwd),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout_bytes, stderr_bytes = await asyncio.wait_for(process.communicate(), timeout=timeout)
        exit_code = process.returncode or 0
        stdout = stdout_bytes.decode("utf-8", errors="replace")
        stderr = stderr_bytes.decode("utf-8", errors="replace")
    except FileNotFoundError:
        exit_code = 127
        stdout = ""
        stderr = f"Command not found: {command[0]}"
    except asyncio.TimeoutError:
        exit_code = 124
        stdout = ""
        stderr = f"Command timed out after {timeout}s"
    except Exception as exc:  # noqa: BLE001
        exit_code = 1
        stdout = ""
        stderr = f"Execution failed: {exc}"

    finished_at = _now_iso()
    return ToolResult(
        tool_name=tool_name,
        command=" ".join(command),
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        started_at_utc=started_at,
        finished_at_utc=finished_at,
    )


async def run_read_only_diagnostics(repo_root: Path, timeout: int = 30) -> List[ToolResult]:
    commands = [
        ("git_status", ["git", "status", "--short"]),
        ("git_branch", ["git", "branch", "--show-current"]),
        ("git_last_commit", ["git", "log", "-1", "--oneline"]),
        ("kubectl_context", ["kubectl", "config", "current-context"]),
        ("kubectl_pods_all", ["kubectl", "get", "pods", "-A"]),
        ("helm_list_all", ["helm", "list", "-A"]),
    ]

    results: List[ToolResult] = []
    for tool_name, command in commands:
        result = await _run_command(command, repo_root, tool_name=tool_name, timeout=timeout)
        results.append(result)
    return results
