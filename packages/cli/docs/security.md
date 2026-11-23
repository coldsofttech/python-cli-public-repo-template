# Security

How `example-cli` protects the people who run it. To report a vulnerability, see [SECURITY.md](../../../SECURITY.md). The command line builds on the [core library](../../core/docs/security.md), so its protections apply here too.

## What the command line does

- **Keeps secrets off the screen.** `run()` prints a one-line message for unexpected errors, shows a traceback only with `--verbose`, and never shows local variables, which can hold tokens and passwords.
- **Separates data from messages.** Results go to stdout and errors to stderr, so piping output never mixes in a message, and `--json` prints one document.
- **Does not send anything anywhere.** The example commands make no network requests and write no files. Keep that visible: a command that does should say so in its help.
- **Honours the environment.** `NO_COLOR` and the `EXAMPLE_CLI_` variables are read; a flag always wins, so a script can override a hostile or stale environment.

## Rules to keep when you add commands

1. **Never take secrets as command line arguments.** Arguments show up in the process list and shell history. Read them from an environment variable, a file (`-H @file`), or a prompt with hidden input.
2. **Do not print secrets**, even with `--verbose`. Log the name of a setting, not its value.
3. **Validate paths and URLs** before using them, and do not follow a user-supplied path outside an intended folder.
4. **Use `subprocess` without a shell** and with a list of arguments. Ruff's `S` rules flag the risky forms.
5. **Keep the exit codes honest.** A failed command must exit non-zero, or scripts will carry on as if it worked.

## The installers and the image

- The Windows setup installs per user by default and asks for administrator rights only for "all users". It changes `PATH` only when asked and removes only what it installed. Set `SIGN_COMMAND` to sign the executable and the setup (see [installer packaging](../../../installer/docs/packaging.md#signing)).
- The Linux packages are system-wide, run non-interactively and never touch a user's home folder.
- The Docker image runs as an unprivileged user with no compilers or pip ([Docker security](../../docker/docs/security.md)).
- Release files carry `SHA256SUMS.txt`, and the image carries build provenance.

## Supply chain

Dependencies are locked in `uv.lock` and installed with `--locked`. `audit-cli.yml` runs `pip-audit` weekly, `security-cli.yml` runs Semgrep and uploads the results to the Security tab, and dependency review blocks vulnerable additions on pull requests. Releases use PyPI trusted publishing, with no stored token.
