# Security

A high-level view of how this project is protected. Each package documents its own protections; start there for detail. To report a vulnerability, see [SECURITY.md](../SECURITY.md).

## Packages

| Package | Protects | Notes |
| --- | --- | --- |
| core (`example-package`) | input, errors and messages, dependencies | [Core security](../packages/core/docs/security.md) |
| CLI (`example-cli`) | secrets you pass, output and logs, the installers | [CLI security](../packages/cli/docs/security.md) |
| Docker | the image: unprivileged user, minimal runtime, no baked-in secrets | [Docker security](../packages/docker/docs/security.md) |

The command line and the Docker image build on the core library, so its protections apply to each of them.

## Repository

- **Branch ruleset.** `main` needs a pull request with a code owner review and resolved conversations, the `ci` and `dependency-review` checks with an up-to-date branch, CodeQL results, squash merge only, and no deletion or force push. See [architecture](architecture.md#branch-governance).
- **Secrets.** Secret scanning with push protection is on, and gitleaks runs in pre-commit. No token is stored for publishing: PyPI uses trusted publishing and GHCR uses the workflow's own token.
- **Workflows.** Workflows ask for read-only permissions by default and raise them per job. Actions are pinned to version tags, kept current by Dependabot with a seven-day cooldown, and `actionlint` and Semgrep's `p/github-actions` rules check them. Values from events are passed through `env`, never expanded inside scripts.
- **Environments.** Each release part publishes from its own GitHub environment, restricted to its tag pattern, so a branch cannot publish and a reviewer can approve each release.

## Supply chain

Dependabot covers Python, Docker and Actions. Each package has its own audit and security workflows (`audit-<package>.yml`, `security-<package>.yml`) that check locked dependencies weekly and run static analysis. Dependency review blocks vulnerable additions on pull requests, and `uv.lock` is committed and installed with `--locked`. Releases are published with trusted publishing, with no stored token (see [releasing](releasing.md)).

## Rules to keep

1. Never commit secrets, and never pass them as command line arguments or build arguments.
2. Keep workflows least-privilege: add a permission to the job that needs it, not to the whole workflow.
3. Keep the library free of output and the command line free of secrets in messages.
4. Add a dependency only when it earns its place, and check its licence and maintenance.
5. Keep the sample `SECURITY.md` contact route working for your repository (private vulnerability reporting enabled).
