# The example command line as a small, non-root image. It runs the same `example-cli` command as
# the Python package; there is no second implementation in here.
#
#   docker run --rm ghcr.io/coldsofttech/python-cli-public-repo-template hello Ada
#
# See packages/docker/docs/docker.md.
#
# Build from the repository root, so both packages are in the context:
#
#   docker build -f packages/docker/Dockerfile -t example-cli .

ARG PYTHON_VERSION=3.13

# --- build: put the packages and their dependencies in a virtual environment ------------------
FROM python:${PYTHON_VERSION}-slim AS build

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /src
COPY packages/core ./packages/core
COPY packages/cli ./packages/cli
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-compile ./packages/core ./packages/cli \
    && /opt/venv/bin/pip uninstall --yes pip

# --- run: the same base without compilers, pip or the sources ----------------------------------
FROM python:${PYTHON_VERSION}-slim AS runtime

ARG VERSION=0.0.0
LABEL org.opencontainers.image.title="example-cli" \
      org.opencontainers.image.description="Python command line tool description." \
      org.opencontainers.image.source="https://github.com/coldsofttech/python-cli-public-repo-template" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.version="${VERSION}"

# A fixed, unprivileged user, so files written to a mounted folder have a predictable owner.
RUN groupadd --system --gid 10001 example \
    && useradd --system --uid 10001 --gid example --no-create-home --shell /usr/sbin/nologin example \
    && mkdir /output \
    && chown example:example /output

COPY --from=build /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    NO_COLOR=1

USER example
WORKDIR /output
VOLUME ["/output"]

ENTRYPOINT ["example-cli"]
CMD ["--help"]
