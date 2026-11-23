# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/).

This file covers the repository as a whole. Each package keeps its own changelog: [core](packages/core/CHANGELOG.md), [cli](packages/cli/CHANGELOG.md), [installer](installer/CHANGELOG.md) and [docker](packages/docker/CHANGELOG.md).

## [Unreleased]

### Added

- The repository is now a uv workspace of two packages, `example-package` (`packages/core`) and `example-cli` (`packages/cli`), that are tested, versioned and released separately.
- A Docker image (`packages/docker`), published to GitHub Container Registry for `linux/amd64` and `linux/arm64`.
- Installers (`installer/`): a Windows setup and portable zip, and Linux deb and rpm packages, of the command line. Sample artwork is in `brand/`.
- An issue template config that points security reports and questions to the right place.
- Continuous integration, audit, security and release workflows are split per package and share composite actions under `.github/actions/`.
