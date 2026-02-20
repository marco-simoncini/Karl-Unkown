from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable

import yaml

from agent.models import EnvironmentName, RiskLevel


RISK_ORDER: Dict[RiskLevel, int] = {"R0": 0, "R1": 1, "R2": 2, "R3": 3}


def _ensure_risk(value: str) -> RiskLevel:
    if value not in RISK_ORDER:
        raise ValueError(f"Invalid risk level: {value}")
    return value  # type: ignore[return-value]


class PolicyEngine:
    def __init__(self, policy_data: Dict[str, Any]):
        self.policy = policy_data
        self.environment_controls = policy_data.get("environment_controls", {})
        self.approval_rules = policy_data.get("approval_rules", [])

    @classmethod
    def from_file(cls, policy_path: Path) -> "PolicyEngine":
        if not policy_path.exists():
            raise FileNotFoundError(f"Policy file not found: {policy_path}")

        with policy_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return cls(data)

    @staticmethod
    def compare_risk(left: RiskLevel, right: RiskLevel) -> int:
        return RISK_ORDER[left] - RISK_ORDER[right]

    def max_auto_risk(self, environment: EnvironmentName) -> RiskLevel:
        env_cfg = self.environment_controls.get(environment, {})
        return _ensure_risk(env_cfg.get("max_auto_risk", "R0"))

    def required_approvals(self, risk: RiskLevel, environment: EnvironmentName) -> int:
        max_required = 0
        for rule in self.approval_rules:
            if self._rule_matches(rule, risk, environment):
                max_required = max(max_required, int(rule.get("required_approvals", 0)))

        if self.compare_risk(risk, self.max_auto_risk(environment)) > 0:
            max_required = max(max_required, 1)
        return max_required

    def requires_approval(self, risk: RiskLevel, environment: EnvironmentName) -> bool:
        return self.required_approvals(risk, environment) > 0

    def _rule_matches(
        self, rule: Dict[str, Any], risk: RiskLevel, environment: EnvironmentName
    ) -> bool:
        when = rule.get("when", {})
        env = when.get("environment")
        if env and env != environment:
            return False

        min_risk = _ensure_risk(when.get("min_risk", "R0"))
        return self.compare_risk(risk, min_risk) >= 0

    def allowed_tools(self) -> Iterable[str]:
        return self.policy.get("tool_controls", {}).get("allowlist", [])

    def denied_tools(self) -> Iterable[str]:
        return self.policy.get("tool_controls", {}).get("denylist", [])
