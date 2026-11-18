from agentgate.models import Finding
from agentgate.sarif import to_sarif


def test_sarif_contains_rule_and_result():
    sarif = to_sarif([
        Finding("AG002", "error", "unapproved MCP server detected", "browser", "server")
    ])
    run = sarif["runs"][0]
    assert run["tool"]["driver"]["rules"][0]["id"] == "AG002"
    assert run["results"][0]["ruleId"] == "AG002"
