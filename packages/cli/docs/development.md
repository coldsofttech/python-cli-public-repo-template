# Development

Working on `example-cli` (`packages/cli`). Repository-wide tooling is in the [root development guide](../../../docs/development.md).

## Layout

```text
src/example_cli/       the command line (Typer app, Rich output, entry point)
tests/unit/            fast tests of commands and output, with typer.testing.CliRunner
tests/integration/     tests of the installed command and of the built (frozen) program
docs/                  this documentation
pyproject.toml         metadata, dependencies and the package's tool configuration
```

## Setup

From the repository root:

```bash
uv sync
uv run pre-commit install --hook-type pre-commit --hook-type post-commit
uv run example-cli --help
```

`uv sync` installs `example-package` from `packages/core` in editable mode, so a change to the library shows in the command at once.

## Everyday commands

Run these from the repository root.

```bash
uv run pytest packages/cli/tests                          # unit tests with coverage (80% minimum)
uv run pytest -m integration packages/cli/tests --no-cov  # integration tests
uv run ruff check packages/cli                            # lint
uv run mypy packages/cli/src                              # type check (strict)
uv build --package example-cli                            # build the sdist and wheel
```

## Tests

- **Unit tests** call the Typer `app` with `CliRunner`: check the exit code, stdout and stderr, and the `--json` output. Strip colour codes before comparing text (GitHub Actions forces colour).
- **Integration tests** start the real program: `python -m example_cli`, the installed console script, and the PyInstaller build (`test_frozen_cli.py`, skipped unless `uv run python installer/scripts/build.py` was run).
- Keep the logic tests in the core package; the command line's tests should be about arguments, output and exit codes.

## Continuous integration

`ci-cli.yml` runs `cli-lint` (Ruff, mypy and pre-commit), `cli-test`, `cli-int-test` and `cli-build` (builds both wheels, `twine check`, checks the CLI wheel does not contain the library, and runs the built wheel). The Windows setup and Linux packages are built by `ci-installer.yml`, and the image by `ci-docker.yml`.

## Before you open a pull request

1. Tests, lint and types pass, and the help text matches the guide.
2. The command is documented under [`guides/cli/`](guides/cli.md) and noted under `[Unreleased]` in [`CHANGELOG.md`](../CHANGELOG.md).
3. The commit message follows [Conventional Commits](https://www.conventionalcommits.org/).
