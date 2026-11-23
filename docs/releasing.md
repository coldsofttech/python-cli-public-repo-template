# Releasing

How a release is routed. Each package's packaging notes hold the steps and set-up for its own release: [core](../packages/core/docs/packaging.md#releasing-to-pypi), [command line](../packages/cli/docs/packaging.md#making-a-release), [installers](../installer/docs/packaging.md#releasing) and [Docker](../packages/docker/docs/packaging.md#releasing-to-ghcr).

## Releases are routed by tag

Publishing a GitHub release runs `release.yml`, and the tag decides what is released. Each part has its own workflow, its own version and its own approval: the job that publishes waits for a reviewer of its environment (Settings > Environments), after everything has been built and tested.

| Tag | Releases | Environment |
| --- | --- | --- |
| `v<version>` | the core library, `example-package`, on PyPI | `core` |
| `cli-v<version>` | the command line, `example-cli`, on PyPI | `cli` |
| `installer-v<version>` | the Windows setup and zip, and the Linux deb and rpm packages; version in `installer/build.toml` | `installer` |
| `docker-v<version>` | the Docker image on GHCR | `docker` |

The tag must equal the version of the package it releases (`installer/build.toml` for the installers). Release the core before the command line, because `example-cli` depends on the `example-package` package on PyPI. Every release that attaches files also gets `SHA256SUMS.txt`.

Before releasing, bump the package's version and move its `[Unreleased]` changelog entries under a version heading. The root [`CHANGELOG.md`](../CHANGELOG.md) covers the repository as a whole.

## Latest markers

GitHub allows one Latest release per repository, so the core owns the badge: after every full release the newest `v<version>` release is marked Latest. Each package also gets its own pointer, a tag and pre-release named `<package>-latest` (`core-latest`, `cli-latest`, `installer-latest`, `docker-latest`) that moves to the newest version and carries its files, so a link to `.../releases/tag/cli-latest` always works. Pre-releases change no marker.

## Pre-releases

Mark the GitHub release as a pre-release to publish without taking `latest` (for the image) or moving any marker. PyPI still receives the version, so use a pre-release version such as `0.2.0rc1` in `__version__`.

## Signing

The installers are signed only when the repository variable `SIGN_COMMAND` is set. See [installer packaging](../installer/docs/packaging.md#signing).

## One-time set-up

1. Run `scripts/apply_repo_settings.py` to create the four environments, restricted to their tag patterns, and the branch ruleset.
2. Add required reviewers to each environment you want an approval step for.
3. On PyPI, add a trusted publisher for each project: workflow `release.yml`, environment `core` or `cli`.
4. After the first image push, make the GHCR package public if anyone should be able to pull it.
