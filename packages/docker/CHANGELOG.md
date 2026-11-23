# Changelog

All notable changes to the Docker image are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- A Docker image that runs the `example-cli` command for `linux/amd64` and `linux/arm64`. It is small, runs as a normal user, and keeps its output in a folder you can mount.
- Releases are published to GitHub Container Registry as a version tag, plus `latest` for full releases, after a reviewer approves them.

### Security

- The image runs as an unprivileged user and holds no compilers or pip, which keeps what can be attacked small.
- The Dockerfile is checked on every change, and the built image is scanned for known vulnerabilities every week.
- Published images carry build provenance.
