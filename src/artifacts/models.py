from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal


@dataclass
class ArtifactRef:
    """Lightweight reference to an artifact stored on disk.

    The string form follows the ``artifact:<id>`` format to make it easy to embed in
    prompts or history logs without pulling in the full payload.
    """

    id: str

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"artifact:{self.id}"

    @classmethod
    def from_string(cls, value: str) -> "ArtifactRef":
        if value.startswith("artifact:"):
            value = value.split(":", 1)[1]
        return cls(id=value)


@dataclass
class ArtifactMeta:
    """Metadata describing an artifact stored on disk."""

    id: str
    kind: Literal["text", "bytes", "json"]
    path: Path
    size: int
    created_at: float
    summary: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "path": str(self.path),
            "size": self.size,
            "created_at": self.created_at,
            "summary": self.summary,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ArtifactMeta":
        return cls(
            id=data["id"],
            kind=data["kind"],
            path=Path(data["path"]),
            size=int(data["size"]),
            created_at=float(data["created_at"]),
            summary=data.get("summary"),
        )

    @property
    def ref(self) -> ArtifactRef:
        return ArtifactRef(self.id)
