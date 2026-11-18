# MVP quality gates

1. **Static import:** Claude- and VS Code-style `mcpServers`/`servers` objects must parse.
2. **Secret safety:** environment values must never enter a baseline or report.
3. **Deterministic diff:** server/tool ordering must not create false findings.
4. **Drift coverage:** command, argument, environment, server, tool, description, and schema changes must detect.
5. **Malformed input:** non-object JSON, invalid types, missing server sections, and oversized files must return exit 2.
6. **Machine output:** JSON and SARIF must contain stable rule IDs and finding fields.
7. **No default execution:** source checkout and `agentgate check` must not launch MCP commands or contact URLs.
8. **Tests:** positive, negative, malformed, boundary, and secret-safety fixtures must pass.
9. **Installation:** a clean virtual environment must install and run the CLI.
10. **Honesty:** documentation must describe runtime and baseline limitations.
