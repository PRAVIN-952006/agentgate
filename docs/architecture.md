# Architecture

```text
MCP config JSON -> bounded JSON loader -> normalized server list
                                                    |
                                                    v
baseline JSON <-> deterministic manifest comparison -> text / JSON / SARIF
```

## Modules

- `contract.py`: bounded JSON loading, format extraction, digests, baselines, drift comparison.
- `models.py`: typed server, tool, and finding structures.
- `cli.py`: init/check commands and exit semantics.
- `sarif.py`: GitHub code-scanning-compatible SARIF representation.

## Design decisions

- No third-party runtime dependencies keep first-use installation and offline operation reliable.
- Environment values are intentionally excluded; only key names are recorded.
- JSON and text are canonicalized before hashing to reduce incidental representation drift.
- Tool lists are sorted so ordering does not create false findings.
- HTTP MCP URLs are not contacted in the MVP.
- Baseline and config parsing are bounded to 10 MiB.
