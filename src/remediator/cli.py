"""Command-line entry point. Argument parsing and output only."""

import argparse
import logging
import sys
from pathlib import Path

from remediator.errors import RemediatorError
from remediator.remediate import RemediationPlan, load_advisories, plan_remediation
from remediator.runner import CommandRunner, SubprocessRunner

DEFAULT_ADVISORIES = Path(__file__).resolve().parents[2] / "advisories" / "advisories.json"
OS_RELEASE_PATH = Path("/etc/os-release")


def build_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(prog="remediator", description=__doc__)
    parser.add_argument("--package", required=True, help="package to check")
    parser.add_argument("--advisories", type=Path, default=DEFAULT_ADVISORIES)
    parser.add_argument("--apply", action="store_true", help="run the upgrade (default: dry run)")
    return parser


def describe(plan: RemediationPlan) -> str:
    """Render a plan as one human-readable line."""
    if plan.action == "not_installed":
        return f"{plan.package}: not installed — nothing to do"
    if plan.action == "none":
        return f"{plan.package} {plan.installed_version}: OK (>= {plan.minimum_safe_version})"
    return (
        f"{plan.package} {plan.installed_version}: VULNERABLE ({plan.advisory_id}, "
        f"needs >= {plan.minimum_safe_version}) -> {' '.join(plan.command or [])}"
    )


def main(argv: list[str] | None = None, runner: CommandRunner | None = None) -> int:
    """Run the CLI and return an exit code."""
    logging.basicConfig(level=logging.WARNING)
    args = build_parser().parse_args(argv)
    runner = runner or SubprocessRunner()
    try:
        advisories = load_advisories(args.advisories)
        os_release = OS_RELEASE_PATH.read_text(encoding="utf-8")
        plan = plan_remediation(args.package, advisories, runner, os_release)
    except RemediatorError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(describe(plan))
    if plan.action == "upgrade" and args.apply and plan.command:
        result = runner.run(plan.command)
        return 0 if result.returncode == 0 else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
