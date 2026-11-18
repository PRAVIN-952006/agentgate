# Adoption and evaluation plan

## Target users

- developers maintaining MCP-enabled repositories;
- open-source maintainers reviewing coding-agent configuration changes;
- security engineers adding an MCP change gate to CI;
- platform engineers standardizing approved agent tools.

## First-run evaluation

Invite a tester to run:

```bash
pipx install .
agentgate init --config .mcp.json --baseline agentgate.baseline.json
agentgate check --config .mcp.json --baseline agentgate.baseline.json
```

Record only opt-in, aggregate feedback: installation success/failure, time to first result, false findings, useful missing findings, supported IDE config formats, and willingness to use it in CI.

Do not collect command arguments, environment values, tool schemas, repository names, or MCP server URLs without explicit consent.

## Adoption signals

Use only verifiable evidence:

- successful independent clean-environment installations;
- external issue reports with reproduction data;
- pull requests that add parser coverage or supported config formats;
- CI usage demonstrated by a public workflow;
- repeated baseline-drift reports;
- maintainer feedback;
- requested improvements that lead to tested releases.

No star, fork, download, telemetry, or testimonial claim should be made until the source can verify it.

## Responsible launch

Before external posting, prepare:

- a copyable 60-second demo;
- screenshots or a recording only if they show real output;
- a comparison page that names mature competing scanners;
- issue templates and good-first-issue candidates;
- a release install/upgrade procedure;
- maintainer review guidance;
- a de-identified beta-tester checklist.
