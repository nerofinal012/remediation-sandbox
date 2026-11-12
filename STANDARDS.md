# Coding Standards — remediation-sandbox

These rules are loaded into every agent step. Changes that break a **MUST** rule are rejected in review.

## Language and style
- **MUST** target Python 3.11+.
- **MUST** pass `ruff check .` with the repo configuration in `pyproject.toml`.
- **MUST** add type hints to every public function and method.
- **SHOULD** keep functions under ~40 lines; split anything longer.
- **SHOULD** give every public function a one-line docstring.

## Architecture
- `versions.py` — pure version parsing/comparison. No I/O.
- `inventory.py` — reads what is installed. All shell access goes through an injected `CommandRunner`.
- `platforms.py` — maps an OS to a package manager and builds upgrade commands. No I/O.
- `remediate.py` — decides what to do (orchestration). No direct subprocess calls.
- `cli.py` — argument parsing and output only.
- New package managers or platforms **MUST** be added in `platforms.py`, not with `if` chains elsewhere.

## Safety
- **MUST NOT** use `shell=True`, `os.system`, or string-built shell commands. Commands are lists of arguments.
- **MUST** keep dry-run as the default. Anything that changes a host requires an explicit `--apply`.
- **MUST NOT** hardcode credentials, tokens, hostnames, IPs or internal URLs.
- **MUST** raise the specific exceptions in `errors.py` instead of bare `Exception`; never swallow exceptions silently.
- **MUST** validate external input (command output, file contents) before using it.

## Testing
- **MUST** add or update tests for every behaviour change; bug fixes need a regression test that fails before the fix.
- **MUST** keep tests free of real subprocess calls — use the `FakeRunner` in `tests/conftest.py`.
- **SHOULD** name tests `test_<unit>_<behaviour>`.

## Pull requests
- Branch name: `agent/<ticket-id>`.
- PR title: `<ticket-id>: <short summary>`.
- PR body must include: summary, acceptance criteria with how each is met, assumptions, risks, test evidence.
