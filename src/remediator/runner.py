"""Command execution boundary. Everything that touches the shell goes through a CommandRunner."""

# Commands are always argument lists and never shell strings, so subprocess is safe here.
import subprocess  # nosec B404
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class CommandResult:
    """Outcome of running a command."""

    returncode: int
    stdout: str
    stderr: str


class CommandRunner(Protocol):
    """Anything that can run a command given as a list of arguments."""

    def run(self, args: list[str]) -> CommandResult:
        """Run the command and return its result."""
        ...


class SubprocessRunner:
    """Real runner used by the CLI. Never uses shell=True."""

    def __init__(self, timeout_seconds: int = 60) -> None:
        self.timeout_seconds = timeout_seconds

    def run(self, args: list[str]) -> CommandResult:
        """Run the command with a timeout and capture its output."""
        # args is a list and shell is never enabled.
        completed = subprocess.run(  # noqa: S603  # nosec B603
            args,
            capture_output=True,
            text=True,
            check=False,
            timeout=self.timeout_seconds,
        )
        return CommandResult(completed.returncode, completed.stdout, completed.stderr)
