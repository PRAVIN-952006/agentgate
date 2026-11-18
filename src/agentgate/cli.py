from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .contract import (
    ContractError,
    baseline_document,
    compare,
    extract_servers,
    load_baseline,
    load_json,
)
from .models import ServerManifest
from .sarif import to_sarif


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentgate",
        description="Approve MCP server configuration and detect tool-manifest drift.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="create an approval baseline")
    init_parser.add_argument("--config", type=Path, required=True)
    init_parser.add_argument("--baseline", type=Path, required=True)

    check_parser = subparsers.add_parser("check", help="compare config against baseline")
    check_parser.add_argument("--config", type=Path, required=True)
    check_parser.add_argument("--baseline", type=Path, required=True)
    check_parser.add_argument("--format", choices=("text", "json", "sarif"), default="text")
    check_parser.add_argument(
        "--fail-on",
        choices=("error", "any"),
        default="error",
        help="return failure for error findings or all findings",
    )
    return parser


def write_baseline(servers: list[ServerManifest], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(baseline_document(servers), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        document = load_json(args.config)
        current = extract_servers(document)
        if args.command == "init":
            write_baseline(current, args.baseline)
            print(f"created baseline: {args.baseline}")
            return 0
        baseline = load_baseline(args.baseline)
        findings = compare(baseline, current)
    except ContractError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps({
            "passed": not (
                any(item.severity == "error" for item in findings)
                if args.fail_on == "error"
                else bool(findings)
            ),
            "findings": [item.as_dict() for item in findings],
        }, indent=2, sort_keys=True))
    elif args.format == "sarif":
        print(json.dumps(to_sarif(findings), indent=2, sort_keys=True))
    else:
        if not findings:
            print("status: PASS")
        else:
            print("status: FAIL")
            for finding in findings:
                print(
                    f"{finding.severity.upper()} {finding.rule} "
                    f"[{finding.server}:{finding.field}] {finding.message}"
                )

    failed = any(item.severity == "error" for item in findings)
    if args.fail_on == "any":
        failed = bool(findings)
    return 1 if failed else 0
