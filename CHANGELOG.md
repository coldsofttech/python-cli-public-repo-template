# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/).

This file covers the repository as a whole. Each package keeps its own changelog: [core](packages/core/CHANGELOG.md) and [cli](packages/cli/CHANGELOG.md).

## [Unreleased]

### Changed

- The repository is now a uv workspace of two packages, `example-package` (`packages/core`) and `example-cli` (`packages/cli`), that are tested, versioned and released separately.
- Continuous integration, audit, security and release workflows are split per package and share composite actions under `.github/actions/`.
