# python-cli-public-repo-template

[![CI](https://github.com/coldsofttech/python-cli-public-repo-template/actions/workflows/ci.yml/badge.svg)](https://github.com/coldsofttech/python-cli-public-repo-template/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/python-cli-public-repo-template)](https://pypi.org/project/python-cli-public-repo-template/)
[![Python versions](https://img.shields.io/pypi/pyversions/python-cli-public-repo-template)](https://pypi.org/project/python-cli-public-repo-template/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![CLI: Typer](https://img.shields.io/badge/CLI-Typer-009688)](https://typer.tiangolo.com/)
[![Output: Rich](https://img.shields.io/badge/output-Rich-blueviolet)](https://github.com/Textualize/rich)
[![License](https://img.shields.io/github/license/coldsofttech/python-cli-public-repo-template)](LICENSE)

A ready-to-use starting point for public Python command line tools on GitHub. It includes a friendly Typer and Rich command line on top of a reusable, typed library, automated testing on Python 3.11 to 3.15, linting, one-step releases to PyPI, and the community and security files a public repository needs.

## What you get

- A command line with `--help`, `--version`, `--verbose`, `--quiet`, `--no-color` and shell completion
- Colored, readable output with Rich that switches off automatically when piped
- A separate typed library, so your logic can be reused outside the command line
- Fast, reproducible setup with [uv](https://docs.astral.sh/uv/)
- Linting, formatting and type checking before every commit and in CI
- Automated tests on Python 3.11 to 3.15 (Ubuntu) and 3.11 (Windows and macOS)
- Publishing to PyPI when you create a GitHub release, with no stored tokens
- Contribution, conduct, support and security-reporting guidelines
- Issue forms, a pull request template and automated dependency updates

## Getting started

1. Click **Use this template** on GitHub and create your new repository.
2. Run the **Init** workflow from the Actions tab and merge the pull request it opens. This fills in your owner and repository name.
3. Rename the example library, the example command line package and the `example-cli` command. See the [development guide](docs/development.md).
4. Add your contact details in `CODE_OF_CONDUCT.md`, delete `.github/workflows/init.yml`, and replace this description.
5. Apply the repository protections by following the [setup guide](docs/repo-setup.md).
6. Install dependencies and commit checks:

   ```bash
   uv sync
   uv run pre-commit install --hook-type pre-commit --hook-type post-commit
   ```

## Installation

Requires Python 3.11 or newer. The recommended way to install a command line tool is in its own isolated environment:

```bash
uv tool install python-cli-public-repo-template
```

Or with pipx:

```bash
pipx install python-cli-public-repo-template
```

To try it without installing:

```bash
uvx --from python-cli-public-repo-template example-cli --help
```

## Usage

```console
$ example-cli --help
$ example-cli --version
$ example-cli hello Ada
Hello, Ada!
```

See the [CLI reference](docs/cli.md) for every command, option and exit code.

> After renaming the command, update the examples above. Once you have written your tool's real commands, replace this example with a short walkthrough of them.

## Development

```bash
git clone https://github.com/coldsofttech/python-cli-public-repo-template.git
cd python-cli-public-repo-template
uv sync
uv run example-cli --help
uv run pytest
```

See the [development guide](docs/development.md) for linting, type checking and releasing.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Please report security issues privately as described in [SECURITY.md](SECURITY.md).

## License

Released under the [MIT License](LICENSE).
