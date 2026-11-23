# `hello`

Print a greeting. It is the command line's example command: replace it with your own, keeping the shape of this page for each command.

```console
$ example-cli hello Ada
Hello, Ada!
```

## Usage

```text
example-cli hello [OPTIONS] [NAME]
```

| Argument or option | Description |
| --- | --- |
| `NAME` | Who to greet. Defaults to `world`. |
| `--json` | Print `{"message": "..."}` as one JSON document instead of the greeting. |
| `--help` | Show help for the command. |

The [global options](../cli.md#global-options) go before the command name: `--quiet` hides the greeting, `--verbose` adds a line on stderr.

## Examples

```console
$ example-cli hello
Hello, world!

$ example-cli hello Ada --json
{
  "message": "Hello, Ada!"
}

$ example-cli --quiet hello Ada --json    # --json still prints, even with --quiet
{
  "message": "Hello, Ada!"
}
```

## Exit codes

| Code | When |
| --- | --- |
| `0` | The greeting was printed. |
| `1` | `NAME` is empty or only whitespace. `Error: name must not be empty` is written to stderr. |
| `2` | Invalid usage, such as an unknown option. |

## How it works

The command in `cli.py` calls [`greet`](../../../../core/docs/guides/python/greeting.md) from the library and prints the result through the Rich console, so the logic can be reused without the terminal.
