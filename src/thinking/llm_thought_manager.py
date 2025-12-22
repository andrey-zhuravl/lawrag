from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

INSTRUCTION = """
When proposing tool calls:
- Use parameters.file_path instead of parameters.path when referring to files.
- Do not inline large outputs; store them as artifacts and refer to them by their refs.
- If you need more detail from an artifact, call `retrieve_artifact` with the ref and optional slice.
"""


@dataclass
class LLMThoughtManager:
    examples: List[Dict[str, Any]]

    def get_instruction(self) -> str:
        return INSTRUCTION

    def get_examples(self) -> List[Dict[str, Any]]:
        updated_examples: list[Dict[str, Any]] = []
        for example in self.examples:
            params = example.get("parameters") or {}
            if "path" in params:
                params["file_path"] = params.pop("path")
            example["parameters"] = params
            updated_examples.append(example)
        return updated_examples
