# Development

Repository-wide tooling and workflow. Each package has its own guide with the commands for that package: [core](../packages/core/docs/development.md) and [command line](../packages/cli/docs/development.md).

## Layout

```text
packages/core/src/example_package/   library: all the logic, never prints or exits (typed)
packages/cli/src/example_cli/        Typer + Rich command line: parses input, calls the library, shows output
packages/*/tests/                    pytest tests (unit/ and integration/) of each package
packages/docker/                     Dockerfile and docs of the container image
installer/                           Windows setup, Linux packages and the PyInstaller build of the command line
brand/                               sample icon and setup artwork
packages/*/pyproject.toml            each package's metadata, dependencies and tool configuration
pyproject.toml                       uv workspace root: dev dependencies and shared tool configuration
uv.lock                              locked dependencies (commit this file)
```

The example names are `example_package` (library), `example_cli` (command line package) and `example-cli` (the command). After creating a repo from this template:

1. Rename `packages/core/src/example_package/` and `packages/cli/src/example_cli/` to your import names, and update the imports in both packages' `src/` and `tests/`.
2. Rename the distributions `example-package` and `example-cli` everywhere they appear (the root and both `pyproject.toml` files, `.github/actions/run-pytest`, `audit-*`, `release-*` and `ci-*` workflows), and in each package's `pyproject.toml` update `[tool.hatch.version]`, `[tool.hatch.build.targets.wheel]`, the `--cov=` options, `known-first-party` and the command in `[project.scripts]`.
3. Update the command name, the `EXAMPLE_CLI_` environment variable prefix and the help text in `packages/cli/src/example_cli/cli.py`, then in `packages/cli/docs/guides/cli.md` and `README.md`, and regenerate `packages/cli/docs/cli-reference.md` (see the [command line guide](../packages/cli/docs/guides/cli.md)).
4. Set the descriptions in both packages' `pyproject.toml`, then run `uv lock`.

Commands, options and exit codes are documented in the [command line guide](../packages/cli/docs/guides/cli.md).

## Tooling

| Purpose | Tool |
| --- | --- |
| Environment, dependencies, build | [uv](https://docs.astral.sh/uv/) with Hatchling |
| Lint and format | Ruff |
| Type checking | mypy (strict) |
| Tests and coverage | pytest with pytest-cov (80% minimum) |

```bash
uv sync                    # create .venv and install dev dependencies of the whole workspace
uv run pytest packages/core/tests      # unit tests of one package with coverage (skips integration tests)
uv run pytest -m integration packages/cli/tests --no-cov   # integration tests of one package
uv run ruff check .        # lint
uv run ruff format .       # format
uv run mypy                # type check
uv build --package example-cli   # build the sdist and wheel of one package
```

## Integration tests

Tests under each package's `tests/integration/` are marked `integration` automatically by that folder's `conftest.py`. They are excluded from the default `pytest` run, and therefore from the pre-commit hook, and run as their own job in CI. Put slower or end-to-end tests there.

## Continuous integration

The `ci` workflow calls one workflow per package (`ci-core`, `ci-cli`) and one for the rest of the repository (`ci-repo`). Each package runs `lint` (Ruff, mypy and pre-commit), `test` (unit tests), `int-test` (tests marked `integration`) and `build` (build and `twine check`). The test jobs run on Python 3.11 to 3.15 on Ubuntu, and on 3.11 on Windows and macOS. On pull requests, `changes` skips the parts a change cannot affect. A final `ci` job gates on all of them and is the single required check in the branch ruleset. Shared steps live in `.github/actions/` (`setup-uv`, `lint-python`, `run-pytest`, `audit-python`, `semgrep`, `check-release-tag`, `attach-release-files`, `update-latest`). The `audit` and `security` workflows follow the same per-package split. `ci-docker` builds the image, and `ci-installer` builds the installers on Windows and Linux and installs and removes them.

## Docker image and installers

The container image is described in [`packages/docker/docs`](../packages/docker/docs/docker.md) and the installers in [`installer/docs/packaging.md`](../installer/docs/packaging.md). When you rename the command, also update `installer/build.toml` (names, the install folder and a new `guid`), `packages/docker/Dockerfile` (user, entry point, labels) and the image name in `.github/workflows/ci-docker.yml`. Replace the sample artwork in `brand/` (see [`brand/README.md`](../brand/README.md)). Build the Linux packages locally with `uv sync --group installer` and `uv run python installer/scripts/build.py --smoke`.

## Releasing

The routing of tags to packages is in [releasing](releasing.md); the steps for each package are in its packaging notes. In short, for PyPI:

Publishing uses [trusted publishing](https://docs.pypi.org/trusted-publishers/), so no API token is stored.

1. On PyPI, add a trusted publisher for each project: workflow `release.yml`, environment `core` for `example-package` and `cli` for `example-cli`.
2. Create the environments `core` and `cli`. The settings script does this and restricts them to `v*` and `cli-v*` tags. It also creates the `installer` and `docker` environments (`installer-v*` and `docker-v*` tags) for the other releases.
3. Bump `__version__` in `packages/<package>/src/<name>/__init__.py` and update that package's `CHANGELOG.md`.
4. Publish a GitHub release tagged `v<version>` for the core, then `cli-v<version>` for the command line (it depends on the core on PyPI). The workflow fails if the tag and version differ.
