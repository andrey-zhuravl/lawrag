from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, List

from artifacts.policy import DEFAULT_ARTIFACT_POLICY, ArtifactPolicy
from artifacts.store import ArtifactStore, LocalArtifactStore
from artifacts.tools import RetrieveArtifactTool
from memory import Context, Observation


@dataclass
class Action:
    """Simple action wrapper that can be executed to produce a result."""

    name: str
    func: Any

    def execute(self) -> Any:  # pragma: no cover - passthrough wrapper
        return self.func()


@dataclass
class Agent:
    artifact_store: ArtifactStore = field(default_factory=lambda: LocalArtifactStore(".artifacts"))
    artifact_policy: ArtifactPolicy = field(default_factory=lambda: DEFAULT_ARTIFACT_POLICY)
    context: Context = field(default_factory=Context)
    tools: List[Any] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.tools:
            self.tools = [RetrieveArtifactTool(self.artifact_store)]

    def actions_to_observations(self, actions: Iterable[Action]) -> List[Observation]:
        observations: list[Observation] = []
        for action in actions:
            result = action.execute()
            output_short, refs = self.artifact_policy.handle_result(result, self.artifact_store)
            observation = Observation.from_raw(action.name, output_short, artifacts=refs)
            self.context.add(observation)
            observations.append(observation)
        return observations

    def build_situation(self, recent: int | None = None) -> str:
        return self.context.format_recent_history(limit=recent)

    def get_observations(self, limit: int | None = None) -> str:
        return self.context.format_recent_history(limit=limit)

    def save_observations_to_redis(self, redis_client: Any, ttl_seconds: int = 3600) -> None:
        if redis_client is None:
            return
        for index, obs in enumerate(self.context.observations):
            key = f"observation:{index}"
            redis_client.setex(
                key,
                ttl_seconds,
                {
                    "action": obs.action_name,
                    "output": obs.output_short,
                    "artifacts": obs.artifacts,
                    "created_at": obs.created_at.isoformat(),
                },
            )

    def list_tools(self) -> list[Any]:
        return self.tools

    def add_tool(self, tool: Any) -> None:
        self.tools.append(tool)
