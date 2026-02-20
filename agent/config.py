from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class Settings:
    app_name: str
    policy_path: Path
    repo_root: Path
    ollama_base_url: str
    ollama_model: str
    ollama_timeout_seconds: float
    command_timeout_seconds: int


def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("AGENT_APP_NAME", "Karl AI Agent MVP"),
        policy_path=Path(
            os.getenv("AGENT_POLICY_PATH", "docs/ai-agent-policy.yaml")
        ).resolve(),
        repo_root=Path(os.getenv("AGENT_REPO_ROOT", os.getcwd())).resolve(),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1").rstrip(
            "/"
        ),
        ollama_model=os.getenv("OLLAMA_MODEL", "gpt-oss:20b"),
        ollama_timeout_seconds=float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "60")),
        command_timeout_seconds=int(os.getenv("AGENT_COMMAND_TIMEOUT_SECONDS", "30")),
    )
