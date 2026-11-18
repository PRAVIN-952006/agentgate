# Responsible launch kit

## One-line description

Approve MCP servers and tool manifests once, then detect drift in CI.

## 60-second demo

```bash
git clone https://github.com/PRAVIN-952006/agentgate.git
cd agentgate
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
agentgate init --config tests/fixtures/mcp.json --baseline /tmp/agentgate.json
agentgate check --config tests/fixtures/mcp.json --baseline /tmp/agentgate.json
```

This is a copyable static-config demo. It does not execute the server.

## Accurate comparison

AgentGate complements MCP scanners. Scanners identify risky descriptions or capabilities. AgentGate records an approved manifest and detects subsequent changes. Neither replaces runtime isolation or server provenance.

## Launch inputs

Do not launch until:

- a real copy-run fixture exists;
- CI workflow runs;
- clean environment verification includes macOS/Linux/Windows where feasible;
- independent tester feedback exists;
- release install instructions are tested;
- a maintenance owner accepts issue review and security reports.
