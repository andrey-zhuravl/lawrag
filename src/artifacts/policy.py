from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, List, Tuple

from .models import ArtifactRef
from .store import ArtifactStore


@dataclass
class ArtifactPolicy:
    """Policy for deciding when to offload data into artifacts."""

    max_inline_chars: int = 2000

    def _should_store(self, result: Any) -> bool:
        if isinstance(result, (dict, list, bytes)):
            return True
        if isinstance(result, str) and len(result) > self.max_inline_chars:
            return True
        return False

    def _summarize(self, result: Any) -> str:
        if isinstance(result, bytes):
            return "bytes payload"
        if isinstance(result, (dict, list)):
            as_json = json.dumps(result, ensure_ascii=False)
            return f"json payload ({len(as_json)} chars)"
        text = str(result)
        if len(text) > 200:
            return text[:200] + "..."
        return text

    def handle_result(self, result: Any, store: ArtifactStore) -> Tuple[str, List[str]]:
        """Return a short output and artifact refs created for the result."""

        refs: list[str] = []
        if self._should_store(result):
            summary = self._summarize(result)
            if isinstance(result, bytes):
                ref, _meta = store.save_bytes(result, summary=summary)
            elif isinstance(result, (dict, list)):
                ref, _meta = store.save_json(result, summary=summary)
            else:
                ref, _meta = store.save_text(str(result), summary=summary)
            refs.append(str(ref))
            output_short = summary
        else:
            output_short = self._summarize(result)
        return output_short, refs


DEFAULT_ARTIFACT_POLICY = ArtifactPolicy()
