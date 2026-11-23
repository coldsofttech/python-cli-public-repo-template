# Development

Working on `example-package` (`packages/core`). Repository-wide tooling is in the [root development guide](../../../docs/development.md).

## Layout

```text
src/example_package/   the library (typed, no printing, no exiting)
tests/unit/            fast tests, run on every commit
tests/integration/     end-to-end tests, marked `integration` by their conftest.py
docs/                  this documentation
pyproject.toml         metadata, dependencies and the package's tool configuration
```

## Setup

From the repository root:

```bash
uv sync                       # one environment for the whole workspace
uv run pre-commit install --hook-type pre-commit --hook-type post-commit
```

## Everyday commands

Run these from the repository root.

```bash
uv run pytest packages/core/tests                          # unit tests with coverage (80% minimum)
uv run pytest -m integration packages/core/tests --no-cov  # integration tests
uv run ruff check packages/core                            # lint
uv run ruff format packages/core                           # format
uv run mypy packages/core/src                              # type check (strict)
uv build --package example-package                         # build the sdist and wheel
```

The package has its own `pyproject.toml` for Ruff, mypy and pytest, so a command pointed at `packages/core` uses that configuration. `known-first-party` in it keeps import sorting the same from the root and from the package.

## Tests

- **Unit tests** (`tests/unit/`) import the package and call it directly. They must be fast and must not touch the network or the user's files.
- **Integration tests** (`tests/integration/`) check the installed package in a fresh interpreter. They are excluded from the default run and from pre-commit, and run as their own job in CI on Python 3.11 to 3.15 (Ubuntu) and 3.11 (Windows and macOS).
- Coverage is measured with branch coverage and must stay at 80% or more (`--cov-fail-under=80`).
- `tests/` is a package (it has `__init__.py`) so test modules with the same name in different packages do not clash. Run one package's tests at a time, as the commands above do.

## Continuous integration

`ci-core.yml` runs these jobs: `core-lint` (Ruff, mypy, pre-commit and a dependency licence check), `core-test`, `core-int-test` and `core-build` (build, `twine check` and a check that the wheel holds only the core). On pull requests, `changes.yml` runs it only when `packages/core/`, the root `pyproject.toml`, `uv.lock` or `.github/` change.

## Before you open a pull request

1. Tests, lint and types pass (the pre-commit hooks run them).
2. Public changes are in `__all__`, documented in the [Python guide](guides/python.md) and noted under `[Unreleased]` in [`CHANGELOG.md`](../CHANGELOG.md).
3. The commit message follows [Conventional Commits](https://www.conventionalcommits.org/).
