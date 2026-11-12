# TICKET-101 — Support RHEL-family hosts (dnf)

**Type:** Story
**Priority:** Medium
**Component:** remediator

## User story
As a platform engineer, I want `remediator` to work on RHEL-family hosts (RHEL, Rocky, Amazon Linux,
Fedora) so that I can use one tool to check and patch vulnerable packages across our whole fleet instead
of only Debian/Ubuntu machines.

## Background
Today `remediator` only supports `apt`. Running it on a RHEL-family host fails with:

```
error: unsupported platform ID='rocky'; supported package managers: apt
```

## Acceptance criteria
1. Hosts whose `/etc/os-release` `ID` or `ID_LIKE` contains `rhel`, `fedora`, `centos` or `amzn` are
   detected as using `dnf`.
2. The installed version is read with `rpm -q --qf %{VERSION} <package>`; a non-zero exit code means
   "not installed".
3. The upgrade command for `dnf` is `dnf upgrade -y <package>`, built as an argument list.
4. Dry-run remains the default — nothing is executed without `--apply`.
5. Unsupported platforms still raise `UnsupportedPlatformError`, and the message lists every supported
   package manager.
6. Existing apt behaviour is unchanged and all existing tests still pass.
7. New tests cover detection, the version query, and the upgrade command for dnf.

## Out of scope
- zypper / SUSE support.
- Pinning to an exact package version.
