# remediation-sandbox

A small, **fictional** vulnerability-remediation tool used as the sandbox repository for an AI Enablement PoC
(Use Case 1: Story-to-Delivery Developer Agent). It contains no production code, real hostnames, credentials,
or customer data.

## What the tool does

`remediator` checks whether a host has a vulnerable version of a package (from `advisories/advisories.json`)
and prints — or, with `--apply`, runs — the command needed to upgrade it to the minimum safe version.

```
python -m remediator.cli --package acme-cli
python -m remediator.cli --package acme-cli --apply
```

It is **dry-run by default**.

## Layout

| Path | Purpose |
|---|---|
| `src/remediator/` | Application code |
| `tests/` | pytest suite |
| `advisories/advisories.json` | Fictional advisory feed (package → minimum safe version) |
| `STANDARDS.md` | Coding standards the agent must follow |
| `tickets/` | Sample tickets fed to the agent |
| `runs/` | Run reports written by the agent (traceability evidence) |
| `.github/workflows/ci.yml` | Lint, tests, security scan and secret scan on every `agent/*` branch |

## Local development

```
pip install -r requirements-dev.txt
ruff check .
pytest
```

## Agent rules

The agent may only push to branches named `agent/<ticket-id>` and may open (never merge) pull requests.
`main` should be protected so that merges require a human.
