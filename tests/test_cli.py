import json
import re
import sys

import pytest
from typer.testing import CliRunner

import example_package
from example_cli.cli import app, run

runner = CliRunner()

ANSI = re.compile(r"\x1b\[[0-9;]*m")


def plain(text: str) -> str:
    """Remove color codes. Typer's help always colors output on GitHub Actions."""
    return ANSI.sub("", text)


def test_help_lists_commands_and_options() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    for text in ("hello", "info", "--version", "--verbose", "--quiet", "--no-color"):
        assert text in plain(result.output)


def test_version() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert example_package.__version__ in result.output


def test_hello_default_name() -> None:
    result = runner.invoke(app, ["hello"])

    assert result.exit_code == 0
    assert "Hello, world!" in result.output


def test_hello_with_name() -> None:
    result = runner.invoke(app, ["hello", "Ada"])

    assert result.exit_code == 0
    assert "Hello, Ada!" in result.output


def test_hello_quiet_suppresses_output() -> None:
    result = runner.invoke(app, ["--quiet", "hello", "Ada"])

    assert result.exit_code == 0
    assert "Hello" not in result.output


def test_hello_verbose_adds_detail() -> None:
    result = runner.invoke(app, ["--verbose", "hello", "Ada"])

    assert result.exit_code == 0
    assert "Greeting 'Ada'" in result.output


def test_hello_empty_name_fails() -> None:
    result = runner.invoke(app, ["hello", " "])

    assert result.exit_code == 1
    assert "must not be empty" in result.output


def test_verbose_and_quiet_conflict() -> None:
    result = runner.invoke(app, ["--verbose", "--quiet", "hello"])

    assert result.exit_code == 2


def test_info_shows_version() -> None:
    result = runner.invoke(app, ["info"])

    assert result.exit_code == 0
    assert example_package.__version__ in result.output


def test_no_color_flag_is_accepted() -> None:
    result = runner.invoke(app, ["--no-color", "hello", "Ada"])

    assert result.exit_code == 0
    assert "Hello, Ada!" in result.output


def test_hello_json() -> None:
    result = runner.invoke(app, ["hello", "Ada", "--json"])

    assert result.exit_code == 0
    assert json.loads(result.output) == {"message": "Hello, Ada!"}


def test_info_json() -> None:
    result = runner.invoke(app, ["info", "--json"])

    assert result.exit_code == 0
    assert json.loads(result.output)["version"] == example_package.__version__


def test_quiet_from_environment() -> None:
    result = runner.invoke(app, ["hello", "Ada"], env={"EXAMPLE_CLI_QUIET": "1"})

    assert result.exit_code == 0
    assert "Hello" not in result.output


def _boom(name: str) -> str:
    raise RuntimeError("boom")


def test_unexpected_error_is_short_by_default(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["example-cli", "hello", "Ada"])
    monkeypatch.setattr("example_cli.cli.greet", _boom)

    with pytest.raises(SystemExit) as exit_info:
        run()

    stderr = capsys.readouterr().err
    assert exit_info.value.code == 1
    assert "RuntimeError: boom" in stderr
    assert "--verbose" in stderr
    assert "Traceback" not in stderr


def test_unexpected_error_shows_traceback_with_verbose(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["example-cli", "--verbose", "hello", "Ada"])
    monkeypatch.setattr("example_cli.cli.greet", _boom)

    with pytest.raises(SystemExit):
        run()

    assert "Traceback" in capsys.readouterr().err
