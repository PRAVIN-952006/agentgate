# Contributing

Keep changes focused. Add a regression fixture for every new drift rule or parser behavior. Do not add network calls or subprocess execution to default `check/init` paths.

Run:

```bash
python -m pytest
ruff check .
mypy src
```
