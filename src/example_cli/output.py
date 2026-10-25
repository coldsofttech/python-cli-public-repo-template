"""Rich consoles shared by every command, so all output is written the same way.

Data goes to ``console`` (stdout) and diagnostics go to ``err_console`` (stderr).
Rich honors the ``NO_COLOR`` environment variable and disables color when output is piped.
"""

from dataclasses import dataclass

from rich.console import Console
from rich.text import Text

console = Console()
err_console = Console(stderr=True)


@dataclass
class Settings:
    """Global output options, set once by the Typer callback."""

    verbose: bool = False


settings = Settings()


def configure(*, no_color: bool, verbose: bool) -> None:
    """Apply global output options."""
    settings.verbose = verbose
    if no_color:
        console.no_color = True
        err_console.no_color = True


def error(message: str) -> None:
    """Print an error message to stderr."""
    err_console.print(Text(f"Error: {message}", style="bold red"))


def print_exception(exc: Exception) -> None:
    """Report an unexpected error: a short message, plus a traceback only with ``--verbose``.

    Local variables are never shown, since they can contain secrets.
    """
    error(f"{type(exc).__name__}: {exc}" if str(exc) else type(exc).__name__)
    if settings.verbose:
        err_console.print_exception(show_locals=False)
    else:
        err_console.print(Text("Run with --verbose for details.", style="dim"))
