from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Iterable, Tuple

from .models import ArtifactMeta, ArtifactRef


class ArtifactStore:
    """Abstract interface for storing artifacts."""

    def save_text(self, content: str, summary: str | None = None) -> Tuple[ArtifactRef, ArtifactMeta]:
        raise NotImplementedError

    def save_bytes(self, content: bytes, summary: str | None = None) -> Tuple[ArtifactRef, ArtifactMeta]:
        raise NotImplementedError

    def save_json(self, content: Any, summary: str | None = None) -> Tuple[ArtifactRef, ArtifactMeta]:
        raise NotImplementedError

    def load(self, ref: ArtifactRef | str) -> Tuple[ArtifactMeta, Any]:
        raise NotImplementedError

    def load_slice(self, ref: ArtifactRef | str, start: int | None = None, stop: int | None = None) -> Tuple[ArtifactMeta, Any]:
        raise NotImplementedError


class LocalArtifactStore(ArtifactStore):
    """Stores artifacts on the local filesystem in a dedicated directory."""

    def __init__(self, base_path: str | Path):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _artifact_paths(self, artifact_id: str, ext: str) -> tuple[Path, Path]:
        data_path = self.base_path / f"{artifact_id}{ext}"
        meta_path = self.base_path / f"{artifact_id}.meta.json"
        return data_path, meta_path

    def _write_meta(self, meta_path: Path, meta: ArtifactMeta) -> None:
        meta_path.write_text(json.dumps(meta.to_dict(), ensure_ascii=False, indent=2))

    def _new_id(self) -> str:
        return uuid.uuid4().hex

    def save_text(self, content: str, summary: str | None = None) -> Tuple[ArtifactRef, ArtifactMeta]:
        artifact_id = self._new_id()
        data_path, meta_path = self._artifact_paths(artifact_id, ".txt")
        encoded = content if isinstance(content, str) else str(content)
        data_path.write_text(encoded)
        meta = ArtifactMeta(
            id=artifact_id,
            kind="text",
            path=data_path,
            size=len(encoded),
            created_at=time.time(),
            summary=summary,
        )
        self._write_meta(meta_path, meta)
        return meta.ref, meta

    def save_bytes(self, content: bytes, summary: str | None = None) -> Tuple[ArtifactRef, ArtifactMeta]:
        artifact_id = self._new_id()
        data_path, meta_path = self._artifact_paths(artifact_id, ".bin")
        data_path.write_bytes(content)
        meta = ArtifactMeta(
            id=artifact_id,
            kind="bytes",
            path=data_path,
            size=len(content),
            created_at=time.time(),
            summary=summary,
        )
        self._write_meta(meta_path, meta)
        return meta.ref, meta

    def save_json(self, content: Any, summary: str | None = None) -> Tuple[ArtifactRef, ArtifactMeta]:
        artifact_id = self._new_id()
        data_path, meta_path = self._artifact_paths(artifact_id, ".json")
        serialized = json.dumps(content, ensure_ascii=False, indent=2)
        data_path.write_text(serialized)
        meta = ArtifactMeta(
            id=artifact_id,
            kind="json",
            path=data_path,
            size=len(serialized.encode("utf-8")),
            created_at=time.time(),
            summary=summary,
        )
        self._write_meta(meta_path, meta)
        return meta.ref, meta

    def _load_meta(self, artifact_id: str) -> ArtifactMeta:
        meta_path = self.base_path / f"{artifact_id}.meta.json"
        if not meta_path.exists():
            raise FileNotFoundError(f"Metadata for artifact {artifact_id} not found")
        data = json.loads(meta_path.read_text())
        return ArtifactMeta.from_dict(data)

    def load(self, ref: ArtifactRef | str) -> Tuple[ArtifactMeta, Any]:
        if isinstance(ref, str):
            ref = ArtifactRef.from_string(ref)
        meta = self._load_meta(ref.id)
        if not meta.path.exists():
            raise FileNotFoundError(f"Artifact data for {ref.id} missing at {meta.path}")

        if meta.kind == "bytes":
            content: Any = meta.path.read_bytes()
        else:
            content = meta.path.read_text()
            if meta.kind == "json":
                content = json.loads(content)
        return meta, content

    def load_slice(self, ref: ArtifactRef | str, start: int | None = None, stop: int | None = None) -> Tuple[ArtifactMeta, Any]:
        meta, content = self.load(ref)
        if isinstance(content, str):
            lines = content.splitlines()
            slice_obj = slice(start, stop)
            return meta, "\n".join(lines[slice_obj])
        if isinstance(content, list):
            slice_obj = slice(start, stop)
            return meta, content[slice_obj]
        return meta, content

    def iter_artifacts(self) -> Iterable[ArtifactMeta]:
        for meta_path in self.base_path.glob("*.meta.json"):
            data = json.loads(meta_path.read_text())
            yield ArtifactMeta.from_dict(data)

    def cleanup(self) -> None:
        for meta in self.iter_artifacts():
            try:
                if meta.path.exists():
                    os.remove(meta.path)
                meta_path = self.base_path / f"{meta.id}.meta.json"
                if meta_path.exists():
                    os.remove(meta_path)
            except OSError:
                continue
