# Documentation

Technical documentation for this project. The top-level [README](../README.md) is for users. Each package has its own `docs/` folder.

## Repository

- [Repository setup](repo-setup.md): protections, ruleset and manual steps for new repos.
- [Development](development.md): layout, tooling, CI and the rename checklist.
- [Architecture](architecture.md): how checks, workflows, governance and releases fit together.
- [Releasing](releasing.md): how tags route to packages, environments and latest markers.
- [Security](security.md): the repository's protections and where each package's are described.

## Packages

| Package | Architecture | Development | Packaging | Security | Guides |
| --- | --- | --- | --- | --- | --- |
| Core library (`packages/core`) | [Architecture](../packages/core/docs/architecture.md) | [Development](../packages/core/docs/development.md) | [Packaging](../packages/core/docs/packaging.md) | [Security](../packages/core/docs/security.md) | [Python guide](../packages/core/docs/guides/python.md) |
| Command line (`packages/cli`) | [Architecture](../packages/cli/docs/architecture.md) | [Development](../packages/cli/docs/development.md) | [Packaging](../packages/cli/docs/packaging.md) | [Security](../packages/cli/docs/security.md) | [Command line guide](../packages/cli/docs/guides/cli.md), [generated reference](../packages/cli/docs/cli-reference.md) |
| Docker image (`packages/docker`) | | | [Packaging](../packages/docker/docs/packaging.md) | [Security](../packages/docker/docs/security.md) | [Docker guide](../packages/docker/docs/docker.md) |
| Installers (`installer`) | | | [Packaging](../installer/docs/packaging.md) | | |
