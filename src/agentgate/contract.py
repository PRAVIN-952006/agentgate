from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .models import Finding, ServerManifest, ToolManifest

MAX_CONFIG_BYTES = 10 * 1024 * 1024


class ContractError(ValueError):
    """Raised when a config or baseline cannot be parsed safely."""


def sha256_json(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_json(path: Path, max_bytes: int = MAX_CONFIG_BYTES) -> dict[str, Any]:
    if not path.is_file():
        raise ContractError(f"input is not a regular file: {path}")
    if path.stat().st_size > max_bytes:
        raise ContractError(f"input exceeds the {max_bytes} byte safety limit")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"could not read valid UTF-8 JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError("top-level JSON value must be an object")
    return value


def extract_servers(document: dict[str, Any]) -> list[ServerManifest]:
    raw = document.get("mcpServers")
    if raw is None:
        raw = document.get("servers")
    if not isinstance(raw, dict):
        raise ContractError("config must contain an object named mcpServers or servers")

    result: list[ServerManifest] = []
    for name, config in raw.items():
        if not isinstance(name, str) or not isinstance(config, dict):
            continue
        url = config.get("url")
        command = config.get("command")
        if isinstance(url, str) and url.strip():
            transport = "http"
            command_value = url.strip()
        elif isinstance(command, str) and command.strip():
            transport = "stdio"
            command_value = command.strip()
        else:
            raise ContractError(f"server {name!r} has neither command nor url")
        args_value = config.get("args", [])
        if not isinstance(args_value, list) or not all(
            isinstance(item, str) for item in args_value
        ):
            raise ContractError(f"server {name!r} args must be an array of strings")
        env = config.get("env", {})
        if not isinstance(env, dict):
            raise ContractError(f"server {name!r} env must be an object")
        tools: list[ToolManifest] = []
        raw_tools = config.get("tools", [])
        if not isinstance(raw_tools, list):
            raise ContractError(f"server {name!r} tools must be an array")
        for tool in raw_tools:
            if not isinstance(tool, dict) or not isinstance(tool.get("name"), str):
                raise ContractError(f"server {name!r} has a tool without a string name")
            description = tool.get("description")
            description_value = description if isinstance(description, str) else ""
            schema = tool.get("inputSchema", tool.get("input_schema", {}))
            if not isinstance(schema, dict):
                raise ContractError(f"tool {tool['name']!r} inputSchema must be an object")
            tools.append(ToolManifest(
                name=tool["name"],
                description_hash=sha256_text(description_value),
                input_schema_hash=sha256_json(schema),
            ))
        result.append(ServerManifest(
            name=name,
            command=command_value,
            args=tuple(args_value),
            env_keys=tuple(sorted(key for key in env if isinstance(key, str))),
            transport=transport,
            tools=tuple(sorted(tools, key=lambda item: item.name)),
        ))
    if not result:
        raise ContractError("config contains no valid MCP server entries")
    return result


def baseline_document(servers: list[ServerManifest]) -> dict[str, Any]:
    return {
        "schema": "agentgate/v1",
        "servers": [server.as_dict() for server in sorted(servers, key=lambda item: item.name)],
    }


def load_baseline(path: Path) -> dict[str, ServerManifest]:
    document = load_json(path)
    if document.get("schema") != "agentgate/v1":
        raise ContractError("unsupported baseline schema")
    raw_servers = document.get("servers")
    if not isinstance(raw_servers, list):
        raise ContractError("baseline servers must be an array")
    result: dict[str, ServerManifest] = {}
    for raw in raw_servers:
        if not isinstance(raw, dict) or not isinstance(raw.get("name"), str):
            raise ContractError("baseline contains an invalid server")
        args = raw.get("args")
        env_keys = raw.get("env_keys")
        tools = raw.get("tools")
        if not isinstance(args, list) or not all(isinstance(item, str) for item in args):
            raise ContractError("baseline server args are invalid")
        if not isinstance(env_keys, list) or not all(isinstance(item, str) for item in env_keys):
            raise ContractError("baseline server env_keys are invalid")
        if not isinstance(raw.get("command"), str) or raw.get("transport") not in {"stdio", "http"}:
            raise ContractError("baseline server command or transport is invalid")
        tool_manifests: list[ToolManifest] = []
        if not isinstance(tools, list):
            raise ContractError("baseline tools are invalid")
        for raw_tool in tools:
            if not isinstance(raw_tool, dict):
                raise ContractError("baseline tool is invalid")
            name = raw_tool.get("name")
            description_hash = raw_tool.get("description_sha256")
            schema_hash = raw_tool.get("input_schema_sha256")
            if not isinstance(name, str):
                raise ContractError("baseline tool fields are invalid")
            if not isinstance(description_hash, str):
                raise ContractError("baseline tool fields are invalid")
            if not isinstance(schema_hash, str):
                raise ContractError("baseline tool fields are invalid")
            tool_manifests.append(ToolManifest(name, description_hash, schema_hash))
        result[raw["name"]] = ServerManifest(
            name=raw["name"],
            command=raw["command"],
            args=tuple(args),
            env_keys=tuple(env_keys),
            transport=raw["transport"],
            tools=tuple(sorted(tool_manifests, key=lambda item: item.name)),
        )
    return result


def compare(
    baseline: dict[str, ServerManifest],
    current: list[ServerManifest],
) -> list[Finding]:
    findings: list[Finding] = []
    current_map = {server.name: server for server in current}
    for name in sorted(set(baseline) - set(current_map)):
        findings.append(Finding(
            "AG001", "warning", "approved MCP server is absent", name, "server"
        ))
    for name in sorted(set(current_map) - set(baseline)):
        findings.append(Finding(
            "AG002", "error", "unapproved MCP server detected", name, "server"
        ))
    for name in sorted(set(baseline) & set(current_map)):
        approved = baseline[name]
        live = current_map[name]
        if approved.transport != live.transport:
            findings.append(Finding(
                "AG003", "error", "server transport changed", name, "transport"
            ))
        if approved.command != live.command:
            findings.append(Finding(
                "AG004", "error", "server command or URL changed", name, "command"
            ))
        if approved.args != live.args:
            findings.append(Finding(
                "AG005", "error", "server arguments changed", name, "args"
            ))
        if approved.env_keys != live.env_keys:
            findings.append(Finding(
                "AG006", "warning", "server environment key set changed", name, "env"
            ))
        approved_tools = {tool.name: tool for tool in approved.tools}
        live_tools = {tool.name: tool for tool in live.tools}
        for tool_name in sorted(set(approved_tools) - set(live_tools)):
            findings.append(Finding(
                "AG007", "warning", "approved MCP tool is absent", name, f"tool:{tool_name}"
            ))
        for tool_name in sorted(set(live_tools) - set(approved_tools)):
            findings.append(Finding(
                "AG008", "error", "unapproved MCP tool detected", name, f"tool:{tool_name}"
            ))
        for tool_name in sorted(set(approved_tools) & set(live_tools)):
            old = approved_tools[tool_name]
            new = live_tools[tool_name]
            if old.description_hash != new.description_hash:
                findings.append(Finding(
                    "AG009",
                    "error",
                    "tool description changed",
                    name,
                    f"tool:{tool_name}.description",
                ))
            if old.input_schema_hash != new.input_schema_hash:
                findings.append(Finding(
                    "AG010",
                    "error",
                    "tool input schema changed",
                    name,
                    f"tool:{tool_name}.inputSchema",
                ))
    return findings
