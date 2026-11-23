"""Checks on the built command line image: it runs, stays unprivileged and keeps its folder."""

from __future__ import annotations

import json
import subprocess
from collections.abc import Callable

Run = Callable[..., subprocess.CompletedProcess[str]]


def test_version_runs(run: Run) -> None:
    result = run("--version")
    assert result.returncode == 0
    assert result.stdout.strip()


def test_command_runs(run: Run) -> None:
    result = run("hello", "Ada")
    assert result.returncode == 0
    assert "Hello, Ada!" in result.stdout


def test_json_output_goes_to_stdout(run: Run) -> None:
    result = run("hello", "Ada", "--json")
    assert result.returncode == 0
    assert json.loads(result.stdout) == {"message": "Hello, Ada!"}


def test_runs_as_unprivileged_user(run: Run) -> None:
    result = run("-u", entrypoint="id")
    assert result.returncode == 0
    assert result.stdout.strip() == "10001"


def test_output_is_writable(run: Run) -> None:
    result = run("-c", "touch /output/x", entrypoint="sh")
    assert result.returncode == 0, result.stderr


def test_color_is_off(run: Run) -> None:
    result = run("NO_COLOR", entrypoint="printenv")
    assert result.stdout.strip() == "1"


def test_failure_is_a_message_not_a_traceback(run: Run) -> None:
    result = run("hello", " ")
    assert result.returncode == 1
    assert "must not be empty" in result.stderr
    assert "Traceback" not in result.stderr


def test_usage_error_exits_with_two(run: Run) -> None:
    assert run("--no-such-option").returncode == 2


def test_no_compiler_and_no_pip_in_the_environment(run: Run) -> None:
    result = run("-c", "command -v gcc cc make; ls /opt/venv/bin/pip* 2>/dev/null", entrypoint="sh")
    assert result.stdout.strip() == ""


def test_image_metadata(docker: str, image: str) -> None:
    inspected = subprocess.run(
        [docker, "image", "inspect", image], capture_output=True, text=True, check=True
    )
    config = json.loads(inspected.stdout)[0]["Config"]
    assert config["User"] == "example"
    assert config["Entrypoint"] == ["example-cli"]
    assert config["Labels"]["org.opencontainers.image.licenses"] == "MIT"
    assert set(config["Volumes"]) == {"/output"}
