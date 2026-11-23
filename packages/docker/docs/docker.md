# Docker

The image runs the same `example-cli` command as the Python package, for headless use on servers and in pipelines. It holds no second implementation: the image installs the `example-package` and `example-cli` packages from this repository.

- **Small:** a slim Python base with only the packages and their dependencies.
- **Non-root:** it runs as user `example` (uid and gid `10001`), with no shell login.
- **Platforms:** `linux/amd64` and `linux/arm64`.

## Running

```bash
docker run --rm ghcr.io/coldsofttech/python-cli-public-repo-template --help
docker run --rm ghcr.io/coldsofttech/python-cli-public-repo-template hello Ada --json
```

The image's entry point is `example-cli`, so everything after the image name is a normal command. Results go to stdout and messages to stderr, so `--json` output can be piped.

## Folders

| Folder | Purpose |
| --- | --- |
| `/output` | The working directory. Mount a folder to keep files the command writes. |

Files are written as uid `10001`. When you mount a host folder, make it writable for that user, or run the container as your own user instead:

```bash
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD/out:/output" ghcr.io/coldsofttech/python-cli-public-repo-template hello Ada
```

## Settings

Options can be set with `EXAMPLE_CLI_` environment variables, for example `-e EXAMPLE_CLI_QUIET=1`. The image sets `NO_COLOR=1`. Command line options win over the environment. Pass secrets as mounted files, not on the command line, and never bake them into an image.

Exit codes are those of the command: `0` success, `1` failure, `2` invalid usage.

## Building

Build from the repository root, so both packages are in the build context:

```bash
docker build -f packages/docker/Dockerfile -t example-cli .
docker build -f packages/docker/Dockerfile --build-arg PYTHON_VERSION=3.12 -t example-cli:py312 .
```

`Dockerfile.dockerignore` limits the build context to `packages/core` and `packages/cli`.

## Publishing

The [CI Docker workflow](../../../.github/workflows/ci-docker.yml) builds the image and checks it on every change to the image or the packages: it starts, it is not root, its folder is writable, and a failure is a short message with exit code 1. Nothing is published.

To publish, create a GitHub release tagged `docker-v<version>`. See [packaging](packaging.md).
