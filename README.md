# AgentGate

AgentGate approves MCP server configuration and detects drift in the tool surface visible to coding agents.

It is change-control software, not an MCP vulnerability certificate. It does not prove that a server is safe, isolate server processes, verify runtime behavior, or authenticate a remote endpoint.

## Problem

MCP servers execute with implicit trust and often inherit developer credentials. Repository configuration can change which server runs, which tools appear, or how a tool description and input schema are interpreted.

AgentGate creates a deterministic approval baseline for:

- server name;
- stdio command or HTTP URL;
- arguments;
- environment key names (never values);
- MCP tool names;
- tool description digests;
- tool input-schema digests.

It detects approved-server removal, unapproved-server addition, command/URL drift, argument drift, environment-key drift, tool removal/addition, description drift, and input-schema drift.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

## Working example

```bash
agentgate init --config .mcp.json --baseline agentgate.baseline.json
agentgate check --config .mcp.json --baseline agentgate.baseline.json
agentgate check --config .mcp.json --baseline agentgate.baseline.json --format json
agentgate check --config .mcp.json --baseline agentgate.baseline.json --format sarif
```

Supported config objects are `mcpServers` or `servers`. Each entry may include `command`, `args`, `env`, `url`, and optional static `tools` records.

Exit status:

- `0`: no failing findings;
- `1`: policy findings;
- `2`: invalid input or malformed baseline.

## CI policy

```bash
agentgate check \
  --config .mcp.json \
  --baseline agentgate.baseline.json \
  --format sarif
```

Use `--fail-on any` when removals or environment-key changes should block even if they are warnings.

## Security and limitations

Baseline creation is static and offline. It never executes a configured server command or stores environment values. HTTP URLs are compared exactly and are not contacted.

Live MCP discovery is not part of the current MVP. A later opt-in implementation must launch servers only with explicit authorization and must isolate them before inherited credentials are available.

See [the threat model](docs/threat-model.md) and [architecture](docs/architecture.md).

## Verification

```bash
python -m pytest
ruff check .
mypy src
```
