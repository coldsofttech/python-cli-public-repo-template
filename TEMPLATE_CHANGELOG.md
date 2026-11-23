# Template changelog

Changes to the template itself. This file is removed when you initialise a repository from the template; your own history belongs in `CHANGELOG.md`.

## [Unreleased]

### Added

- The repository is a uv workspace of two packages, `example-package` (`packages/core`) and `example-cli` (`packages/cli`), each with its own `pyproject.toml`, tests, changelog, README and documentation.
- A Docker image (`packages/docker`) with image tests, released to GitHub Container Registry.
- Installers (`installer/`): a Windows setup and zip (PyInstaller and NSIS) and Linux deb and rpm packages (nfpm), with sample artwork in `brand/`.
- Per-package CI, audit, security and release workflows, a `changes` workflow that limits pull requests to the parts they touch, and shared composite actions under `.github/actions/`.
- Releases routed by tag (`v`, `cli-v`, `installer-v`, `docker-v`), each with its own environment, and `<package>-latest` markers.
- Documentation for each package and for the repository: architecture, development, packaging, security, releasing and guides.
- An issue template config that points security reports and questions to the right place.

### Changed

- Settings script creates one release environment per package instead of `pypi`.

### Removed

- The generated CLI reference (`docs/cli-reference.md`) and its CI check.

## [0.1.0] - 2026-11-20

### Added

- The first version of the template: a Typer and Rich command line over a typed library, tests, linting, type checking, pre-commit hooks, CI, dependency review, audit and release to PyPI, and the community and security files a public repository needs.
