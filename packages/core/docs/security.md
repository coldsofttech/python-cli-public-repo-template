# Security

How `example-package` protects its users, and what to keep doing when you add to it. To report a vulnerability, see [SECURITY.md](../../../SECURITY.md).

## What the library does

- **Validates input.** Functions check their arguments and raise a clear exception (`ValueError` for the example) instead of continuing with bad data.
- **Never prints or exits.** Nothing is written to the console by the library, so a secret that reaches it cannot leak through its output. The front end decides what to show.
- **No hidden side effects.** The example library touches no files, network or environment. Keep that true unless a function's purpose needs it, and document it when it does.
- **Typed.** `mypy --strict` catches a class of mistakes (missing `None` checks, wrong types) before they ship.

## Rules to keep when you extend it

1. **Treat all input as untrusted.** Validate values and sizes; never build shell commands, SQL or file paths from them with string formatting.
2. **Keep secrets out of messages.** Exception messages and logs must not contain tokens, passwords or whole request bodies. Name the field, not the value.
3. **Use the standard library or a vetted dependency.** Every dependency is attack surface. Add one only when needed, pin it through `uv.lock` and keep `pip-licenses` and the audit passing.
4. **Do not use `eval`, `exec` or `pickle` on external data**, and do not disable TLS verification. Ruff's `S` rules (flake8-bandit) flag the common mistakes.
5. **Write files safely.** If you add file output, create files with restrictive permissions, never follow user-supplied paths outside an intended folder, and write to a temporary name before renaming.

## Supply chain

- Dependencies are locked in `uv.lock` and CI installs with `--locked`.
- `audit-core.yml` runs `pip-audit` on the locked dependencies weekly, and dependency review blocks vulnerable additions on pull requests.
- `security-core.yml` runs Semgrep (`p/python`, `p/owasp-top-ten`) and uploads the results to the Security tab.
- Releases are built in CI and published with trusted publishing: no token is stored, and the publishing job needs an approved environment.
