# Packaging and releasing

## Versions

The image has its own version, kept in [`CHANGELOG.md`](../CHANGELOG.md) and the release tag `docker-v<version>`. It is separate from the packages inside it: raise it when a bundled package or the Dockerfile changes.

## Releasing to GHCR

1. Update the image's `CHANGELOG.md` in a pull request and merge it.
2. Create the `docker` environment (the settings script does this and restricts it to `docker-v*` tags) and, if you want a reviewer, add required reviewers to it.
3. Publish a GitHub release tagged `docker-v<version>`. The `Release Docker` workflow waits for the environment's approval, builds `linux/amd64` and `linux/arm64`, and pushes `ghcr.io/<owner>/<repository>:<version>` (and `latest`, unless the release is marked as a pre-release) with provenance. It uses the workflow's own token, so no secret is needed.
4. After the first push, make the package public in the repository's package settings if you want anyone to pull it.

The workflow then moves the `docker-latest` tag and pre-release to the new version.

## The image

- **User.** A fixed system user and group `example` (uid and gid `10001`) with no home folder and no login shell, so files written to a mounted folder have a predictable owner.
- **Entry point.** `ENTRYPOINT ["example-cli"]` with `CMD ["--help"]`.
- **Labels.** The OCI labels (title, description, source, license and `VERSION`) are set so registries show the right details.
- **Build.** Two stages: the first installs both packages into a virtual environment, the second copies only that environment onto the same base, with no pip in the environment and no sources.
