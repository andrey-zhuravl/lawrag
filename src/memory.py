from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Iterable, List


@dataclass
class Observation:
    """Agent observation after executing an action."""

    action_name: str
    output_short: str
    artifacts: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def from_raw(cls, action_name: str, output_short: str, artifacts: Iterable[str] | None = None) -> "Observation":
        return cls(action_name=action_name, output_short=output_short, artifacts=list(artifacts or []))

    def to_json_fields(self) -> dict[str, Any]:
        return {
            "action": self.action_name,
            "output": self.output_short,
            "artifacts": list(self.artifacts),
            "created_at": self.created_at.isoformat(),
        }

    def to_json(self) -> dict[str, Any]:
        return self.to_json_fields()


@dataclass
class Context:
    """Rolling context of observations used to build prompts."""

    observations: List[Observation] = field(default_factory=list)

    def add(self, observation: Observation) -> None:
        self.observations.append(observation)

    def format_recent_history(self, limit: int | None = None) -> str:
        items = self.observations[-limit:] if limit else self.observations
        lines: list[str] = []
        for obs in items:
            refs = f" refs: {', '.join(obs.artifacts)}" if obs.artifacts else ""
            lines.append(f"[{obs.action_name}] {obs.output_short}{refs}")
        return "\n".join(lines)
