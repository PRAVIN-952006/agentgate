# Threat model

## Assets

- Trust decisions represented by an approved baseline.
- MCP server commands, URLs, arguments, and environment key names.
- Tool names, descriptions, and input schemas.
- Developer credentials if live discovery is added.
- CI result integrity and developer expectations.

## Trust boundaries

The MCP config and baseline are untrusted local inputs. The AgentGate parser is trusted application code. No network or subprocess boundary is crossed in the MVP. The output consumer may be an IDE, terminal, CI system, or code-scanning API.

## Threat actors

- A malicious repository or maintainer change that adds an MCP server or tool.
- A compromised MCP package that changes command resolution or tool description.
- A developer accidentally introducing schema drift or secret-key drift.
- A malicious baseline edit or CI artifact substitution.

## Abuse cases and mitigations

| Abuse case | Mitigation | Residual risk |
| --- | --- | --- |
| Oversized config exhausts memory | 10 MiB file-size limit before parsing | Deep JSON nesting is still delegated to the runtime parser |
| Malformed config creates false pass | Explicit object/list validation | Valid but semantically incomplete server configs may pass |
| Environment secret is written to baseline | Only env key names are retained | Secret values may exist in the source config and require repository hygiene |
| Tool schema is changed after approval | Canonical JSON digest detects drift | Tool behavior can change without schema/description changes |
| Server package is mutable | Command/argument drift is detected, but no package identity verification exists | Package resolution and update behavior are a residual supply-chain risk |
| Baseline is edited without review | Baseline is a normal reviewed repository file | AgentGate does not authenticate repository policy |
| Live server code steals credentials | Live discovery is deliberately unsupported in MVP | Future live discovery requires isolation and explicit authorization |

## Security assumptions

The baseline is changed only through repository review. The source config is not a security boundary by itself. CI has an adequate trust boundary and does not execute unreviewed repository code before policy evaluation.

## Residual risk

AgentGate detects configuration and manifest drift. It cannot prove server implementation, runtime behavior, model interpretation, or credential isolation. A passing result means only that the parsed current configuration matches the baseline.
