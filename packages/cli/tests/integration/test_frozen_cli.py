"""Smoke test of the built command line: it starts and answers. Needs the installer build."""

import subprocess
from pathlib import Path

import example_package
from tests.frozen import locate, skip_if_blocked

FOLDER = "example-cli"
SCRIPT = "example-cli"


def _run(exe: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            [str(exe), *arguments],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
            check=False,
        )
    except OSError as error:
        skip_if_blocked(error, exe)
        raise


def test_reports_its_version() -> None:
    result = _run(locate(FOLDER, SCRIPT), "--version")

    assert result.returncode == 0
    assert example_package.__version__ in result.stdout


def test_runs_a_command() -> None:
    result = _run(locate(FOLDER, SCRIPT), "hello", "Ada")

    assert result.returncode == 0
    assert "Hello, Ada!" in result.stdout


def test_reports_errors_with_a_failing_exit_code() -> None:
    result = _run(locate(FOLDER, SCRIPT), "hello", " ")

    assert result.returncode == 1
    assert "must not be empty" in result.stderr
