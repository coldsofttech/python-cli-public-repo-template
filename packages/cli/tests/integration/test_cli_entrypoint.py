import subprocess
import sys
from pathlib import Path

import example_package


def _run(*command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, check=False)


def test_module_entrypoint() -> None:
    result = _run(sys.executable, "-m", "example_cli", "--version")

    assert result.returncode == 0
    assert example_package.__version__ in result.stdout


def test_console_script() -> None:
    script = Path(sys.executable).parent / (
        "example-cli.exe" if sys.platform == "win32" else "example-cli"
    )

    result = _run(str(script), "hello", "Ada")

    assert result.returncode == 0
    assert "Hello, Ada!" in result.stdout


def test_errors_go_to_stderr() -> None:
    result = _run(sys.executable, "-m", "example_cli", "hello", " ")

    assert result.returncode == 1
    assert "must not be empty" in result.stderr
    assert result.stdout == ""
