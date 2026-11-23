# example-cli Docker image

[![CI](https://github.com/coldsofttech/python-cli-public-repo-template/actions/workflows/ci.yml/badge.svg)](https://github.com/coldsofttech/python-cli-public-repo-template/actions/workflows/ci.yml)
[![GHCR](https://img.shields.io/badge/ghcr.io-coldsofttech%2Fpython--cli--public--repo--template-blue?logo=docker&logoColor=white)](https://github.com/coldsofttech/python-cli-public-repo-template/pkgs/container/python-cli-public-repo-template)
[![Platforms](https://img.shields.io/badge/platforms-linux%2Famd64%20%7C%20linux%2Farm64-blue)](docs/docker.md)
[![Non-root](https://img.shields.io/badge/runs%20as-non--root-green)](docs/security.md)
[![License](https://img.shields.io/github/license/coldsofttech/python-cli-public-repo-template)](LICENSE)

The `example-cli` command as a small container image, for servers and pipelines, with nothing to install except Docker.

```sh
docker run --rm ghcr.io/coldsofttech/python-cli-public-repo-template hello Ada
```

It is the same `example-cli` command as the Python package, so everything after the image name works as it does in a terminal.

| Folder | Purpose |
| --- | --- |
| `/output` | The working directory. Mount a folder to keep files the command writes. |

The image runs as a normal user (uid `10001`), supports `linux/amd64` and `linux/arm64`, and carries no compilers or pip in its application environment.

## Learn more

- [Docker guide](docs/docker.md): folders, settings, building and publishing
- [Security](docs/security.md): running the container safely
- [Packaging and releasing](docs/packaging.md)
- [Changelog](CHANGELOG.md)

## License

MIT. See [LICENSE](LICENSE).
