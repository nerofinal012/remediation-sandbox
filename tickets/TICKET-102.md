# TICKET-102 — Crash when installed version has a Debian revision suffix

**Type:** Bug
**Priority:** High
**Component:** remediator
**Reported by:** on-call (fictional)

## Description
Running the dry-run check on an Ubuntu 22.04 host crashes instead of reporting the package status.
Other hosts in the same batch worked. The failing host has `acme-cli` installed from the distro
repository rather than from our internal mirror.

## Steps to reproduce
1. On an Ubuntu host with `acme-cli` installed from the Ubuntu archive, run:
   `python -m remediator.cli --package acme-cli`
2. Observe the crash below.

## Expected
The tool reports `acme-cli 2.58.0-1ubuntu1: VULNERABLE (FAKE-2026-0101, needs >= 2.61.0)` and suggests
the upgrade command.

## Actual
```
Traceback (most recent call last):
  File "src/remediator/cli.py", line 45, in main
    plan = plan_remediation(args.package, advisories, runner, os_release)
  File "src/remediator/remediate.py", line 71, in plan_remediation
    if is_vulnerable(installed, advisory.minimum_safe_version):
       ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "src/remediator/versions.py", line 18, in is_vulnerable
    return parse_version(installed) < parse_version(minimum_safe)
           ~~~~~~~~~~~~~^^^^^^^^^^^
  File "src/remediator/versions.py", line 13, in parse_version
    return tuple(int(part) for part in cleaned.split("."))
  File "src/remediator/versions.py", line 13, in <genexpr>
    return tuple(int(part) for part in cleaned.split("."))
                 ~~~^^^^^^
ValueError: invalid literal for int() with base 10: '0-1ubuntu1'
```

## Notes
- `dpkg-query -W -f='${Version}' acme-cli` on the failing host prints `2.58.0-1ubuntu1`.
- Some packages also report an epoch, e.g. `1:2.58.0-1ubuntu1`.
- A malformed version should produce a clear `InvalidVersionError`, never a raw `ValueError`.
