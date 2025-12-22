from __future__ import annotations

import sys
import tomllib
from pathlib import Path

BASE_DIR = Path(__file__).parent
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from agent import Agent  # type: ignore  # noqa: E402
from artifacts.store import LocalArtifactStore  # type: ignore  # noqa: E402


def load_config(path: str | Path = "config.toml") -> dict:
    config_path = Path(path)
    if config_path.exists():
        with config_path.open("rb") as f:
            return tomllib.load(f)
    return {"artifacts": {"dir": ".artifacts"}}


def main() -> None:
    config = load_config()
    artifacts_dir = config.get("artifacts", {}).get("dir", ".artifacts")
    artifact_store = LocalArtifactStore(artifacts_dir)
    agent = Agent(artifact_store=artifact_store)
    print(f"Artifact store initialized at: {artifact_store.base_path}")
    print(f"Available tools: {[tool.name for tool in agent.list_tools()]}")


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    main()
