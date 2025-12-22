from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .store import ArtifactStore
from .models import ArtifactRef


@dataclass
class RetrieveArtifactTool:
    """Tool that retrieves artifact content by ref.

    Parameters:
        ref: string id in form ``artifact:<id>``
        slice: optional [start, end) slice of lines or list elements.
    """

    artifact_store: ArtifactStore
    name: str = "retrieve_artifact"

    def __call__(self, ref: str, slice: Optional[tuple[int | None, int | None]] = None) -> Dict[str, Any]:
        start = slice[0] if slice else None
        stop = slice[1] if slice else None
        meta, content = self.artifact_store.load_slice(ref, start=start, stop=stop)
        return {
            "ref": str(meta.ref),
            "kind": meta.kind,
            "slice": slice,
            "content": content,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": "Retrieve artifact content using a ref produced earlier.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ref": {"type": "string"},
                    "slice": {
                        "type": "array",
                        "items": {"type": "integer", "nullable": True},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "Optional start and end indexes to limit the response.",
                    },
                },
                "required": ["ref"],
            },
        }
