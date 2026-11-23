# Packaging and releasing

How `example-package` is built and published to PyPI.

## What is built

`uv build --package example-package` writes a source distribution and a wheel to `dist/`. Hatchling builds them from `packages/core/pyproject.toml`: the wheel contains `example_package` only (`[tool.hatch.build.targets.wheel]`), plus the licence and the typing marker. CI checks the metadata with `twine check --strict` and fails if the wheel contains the command line.

## Versions

The version is `__version__` in `src/example_package/__init__.py`. The project follows [Semantic Versioning](https://semver.org/). The package's own history is [`CHANGELOG.md`](../CHANGELOG.md); the command line, installers and image have theirs.

## Releasing to PyPI

Publishing uses [trusted publishing](https://docs.pypi.org/trusted-publishers/), so no API token is stored.

One-time set-up:

1. On PyPI, add a trusted publisher for `example-package`: this repository, workflow `release.yml`, environment `core`.
2. Create the GitHub environment `core`. `scripts/apply_repo_settings.py` does this and restricts it to `v*` tags; add required reviewers if you want an approval step.

Each release:

1. Bump `__version__` and move the `[Unreleased]` entries of `CHANGELOG.md` under a version heading, in a pull request.
2. After it is merged, publish a GitHub release tagged `v<version>` (for `0.2.0`, the tag `v0.2.0`). Mark it as a pre-release to publish without moving the Latest badge.
3. `release.yml` checks the tag against the version, builds in one job, then publishes from a second job that waits for the `core` environment and is the only one with the `id-token` permission.
4. The files are attached to the release with `SHA256SUMS.txt`, and the `core-latest` tag and pre-release move to the new version.

Release the core **before** the command line: `example-cli` depends on `example-package` on PyPI.
