import json

from agentgate.cli import main


def write_config(path):
    path.write_text(json.dumps({
        "mcpServers": {
            "filesystem": {
                "command": "python",
                "args": ["server.py"],
                "env": {"API_TOKEN": "secret-value"},
            }
        }
    }))


def test_init_does_not_store_environment_values(tmp_path):
    config = tmp_path / "mcp.json"
    baseline = tmp_path / "agentgate.json"
    write_config(config)
    assert main(["init", "--config", str(config), "--baseline", str(baseline)]) == 0
    text = baseline.read_text()
    assert "secret-value" not in text
    assert "API_TOKEN" in text


def test_check_passes_for_unmodified_config(tmp_path):
    config = tmp_path / "mcp.json"
    baseline = tmp_path / "agentgate.json"
    write_config(config)
    assert main(["init", "--config", str(config), "--baseline", str(baseline)]) == 0
    assert main([
        "check", "--config", str(config), "--baseline", str(baseline), "--format", "json"
    ]) == 0


def test_check_detects_unapproved_server(tmp_path):
    config = tmp_path / "mcp.json"
    baseline = tmp_path / "agentgate.json"
    write_config(config)
    main(["init", "--config", str(config), "--baseline", str(baseline)])
    config.write_text(json.dumps({
        "mcpServers": {
            "filesystem": {
                "command": "python",
                "args": ["server.py"],
            },
            "browser": {"command": "browser"},
        }
    }))
    assert main([
        "check", "--config", str(config), "--baseline", str(baseline)
    ]) == 1
