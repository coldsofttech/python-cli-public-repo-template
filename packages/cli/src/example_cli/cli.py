"""Command line interface built on Typer and Rich. It only parses input and shows output."""

import platform
from dataclasses import dataclass
from typing import Annotated

import typer
from rich.table import Table
from rich.text import Text

from example_cli import output
from example_package import __version__, greet

app = typer.Typer(
    name="example-cli",
    help="Example command line tool built on [bold]example_package[/bold].",
    no_args_is_help=True,
    rich_markup_mode="rich",
    # run() reports errors briefly; Typer's own traceback would show local variables.
    pretty_exceptions_enable=False,
)

JsonOption = Annotated[bool, typer.Option("--json", help="Output as JSON.")]


@dataclass
class State:
    """Global options shared with every command through the Typer context."""

    verbose: bool = False
    quiet: bool = False


def _show_version(value: bool) -> None:
    if value:
        output.console.print(f"example-cli {__version__}")
        raise typer.Exit


def _state(ctx: typer.Context) -> State:
    state = ctx.obj
    # Set by the callback below, so this only narrows the type.
    assert isinstance(state, State)  # noqa: S101
    return state


@app.callback()
def main(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-V",
            callback=_show_version,
            is_eager=True,
            help="Show the version and exit.",
        ),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", envvar="EXAMPLE_CLI_VERBOSE", help="Show extra detail."),
    ] = False,
    quiet: Annotated[
        bool,
        typer.Option("--quiet", "-q", envvar="EXAMPLE_CLI_QUIET", help="Only show errors."),
    ] = False,
    no_color: Annotated[
        bool,
        typer.Option("--no-color", envvar="EXAMPLE_CLI_NO_COLOR", help="Disable colored output."),
    ] = False,
) -> None:
    """Options that apply to every command."""
    if verbose and quiet:
        raise typer.BadParameter("--verbose and --quiet cannot be used together.")
    output.configure(no_color=no_color, verbose=verbose)
    ctx.obj = State(verbose=verbose, quiet=quiet)


@app.command()
def hello(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument(help="Who to greet.")] = "world",
    json_output: JsonOption = False,
) -> None:
    """Print a greeting."""
    state = _state(ctx)
    try:
        message = greet(name)
    except ValueError as exc:
        output.error(str(exc))
        raise typer.Exit(code=1) from exc
    if state.verbose:
        output.err_console.print(Text(f"Greeting {name!r}", style="dim"))
    if json_output:
        output.console.print_json(data={"message": message})
    elif not state.quiet:
        output.console.print(Text(message, style="bold green"))


@app.command()
def info(json_output: JsonOption = False) -> None:
    """Show version and environment details."""
    details = {
        "version": __version__,
        "python": platform.python_version(),
        "platform": platform.platform(),
    }
    if json_output:
        output.console.print_json(data=details)
        return
    table = Table(title="example-cli", show_header=False)
    for key, value in details.items():
        table.add_row(key.capitalize(), value)
    output.console.print(table)


def run() -> None:
    """Console script entry point: run the app and report unexpected errors briefly."""
    try:
        app()
    except Exception as exc:
        output.print_exception(exc)
        raise SystemExit(1) from exc
