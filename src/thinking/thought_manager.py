from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List

from artifacts.tools import RetrieveArtifactTool


@dataclass
class ThoughtManager:
    tools: List[Any] = field(default_factory=list)

    def register_default_tools(self, artifact_store: Any) -> None:
        self.tools.append(RetrieveArtifactTool(artifact_store))

    def get_tools(self) -> List[Any]:
        return self.tools
