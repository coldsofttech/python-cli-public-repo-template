# Security

- **Unprivileged.** The container runs as uid `10001`, never as root. Do not add `--privileged` or extra capabilities; the command needs none.
- **Small surface.** The runtime image holds only Python, the two packages and their dependencies: no compilers, no pip, no sources.
- **Secrets.** Pass them as mounted files (`-v "$PWD/secret:/run/secrets/token:ro"`), not as arguments, which show up in the process list and shell history. Never bake secrets into an image or a build argument.
- **Read-only.** You can run it with `--read-only` and a mounted `/output`.
- **Scanning.** The Dockerfile is checked by Semgrep and Trivy on every change, and the built image is scanned by Trivy every week. Findings go to the repository's Security tab.
- **Provenance.** Published images carry build provenance, so you can check they were built from this repository's workflow.

To report a vulnerability, see the repository's [security policy](../../../SECURITY.md).
