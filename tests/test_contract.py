from agentgate.contract import (
    ContractError,
    baseline_document,
    compare,
    extract_servers,
)


def server_config(command: str = "python") -> dict:
    return {
        "mcpServers": {
            "filesystem": {
                "command": command,
                "args": ["server.py"],
                "env": {"API_TOKEN": "must-not-be-stored"},
                "tools": [{
                    "name": "read_file",
                    "description": "Read a file",
                    "inputSchema": {
                        "type": "object",
                        "properties": {"path": {"type": "string"}},
                        "required": ["path"],
                    },
                }],
            }
        }
    }


def test_init_and_unmodified_check():
    current = extract_servers(server_config())
    baseline = baseline_document(current)
    findings = compare({
        server.name: server
        for server in current
    }, current)
    assert findings == []
    assert baseline["schema"] == "agentgate/v1"
    assert "must-not-be-stored" not in repr(baseline)


def test_unapproved_server():
    approved = extract_servers(server_config())
    current = extract_servers({
        "mcpServers": {
            "filesystem": server_config()["mcpServers"]["filesystem"],
            "browser": {"command": "browser"},
        }
    })
    findings = compare({server.name: server for server in approved}, current)
    assert any(item.rule == "AG002" and item.server == "browser" for item in findings)


def test_command_drift():
    approved = extract_servers(server_config("python"))
    current = extract_servers(server_config("node"))
    findings = compare({server.name: server for server in approved}, current)
    assert any(item.rule == "AG004" for item in findings)


def test_tool_description_drift():
    approved = extract_servers(server_config())
    changed = server_config()
    changed["mcpServers"]["filesystem"]["tools"][0]["description"] = "Read any file"
    current = extract_servers(changed)
    findings = compare({server.name: server for server in approved}, current)
    assert any(item.rule == "AG009" for item in findings)


def test_tool_schema_drift():
    approved = extract_servers(server_config())
    changed = server_config()
    changed["mcpServers"]["filesystem"]["tools"][0]["inputSchema"]["required"] = []
    current = extract_servers(changed)
    findings = compare({server.name: server for server in approved}, current)
    assert any(item.rule == "AG010" for item in findings)


def test_missing_config_section_is_rejected():
    try:
        extract_servers({"other": {}})
    except ContractError:
        return
    raise AssertionError("missing MCP config section should be rejected")


def test_oversized_config_is_rejected(tmp_path):
    from agentgate.contract import load_json

    path = tmp_path / "large.json"
    path.write_text("{}")
    try:
        load_json(path, max_bytes=1)
    except ContractError:
        return
    raise AssertionError("oversized config should be rejected")
