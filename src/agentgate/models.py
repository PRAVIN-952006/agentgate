from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolManifest:
    name: str
    description_hash: str
    input_schema_hash: str

    def as_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "description_sha256": self.description_hash,
            "input_schema_sha256": self.input_schema_hash,
        }


@dataclass(frozen=True)
class ServerManifest:
    name: str
    command: str
    args: tuple[str, ...]
    env_keys: tuple[str, ...]
    transport: str
    tools: tuple[ToolManifest, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "command": self.command,
            "args": list(self.args),
            "env_keys": list(self.env_keys),
            "transport": self.transport,
            "tools": [tool.as_dict() for tool in self.tools],
        }


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    message: str
    server: str
    field: str

    def as_dict(self) -> dict[str, str]:
        return {
            "rule": self.rule,
            "severity": self.severity,
            "message": self.message,
            "server": self.server,
            "field": self.field,
        }
