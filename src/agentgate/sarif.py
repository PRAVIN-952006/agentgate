from __future__ import annotations

from typing import Any

from .models import Finding


def to_sarif(findings: list[Finding]) -> dict[str, Any]:
    rules: dict[str, dict[str, Any]] = {}
    results: list[dict[str, Any]] = []
    for finding in findings:
        rules.setdefault(finding.rule, {
            "id": finding.rule,
            "name": finding.rule,
            "shortDescription": {"text": finding.message},
        })
        results.append({
            "ruleId": finding.rule,
            "level": "error" if finding.severity == "error" else "warning",
            "message": {"text": finding.message},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": "MCP configuration"},
                    "region": {"startLine": 1},
                }
            }],
            "properties": {"server": finding.server, "field": finding.field},
        })
    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": "AgentGate",
                    "informationUri": "https://github.com/PRAVIN-952006/agentgate",
                    "rules": list(rules.values()),
                }
            },
            "results": results,
        }],
    }
