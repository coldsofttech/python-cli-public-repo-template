# Installer packaging and releasing

How the installers are built and released: a Windows setup and portable zip of the command line, and its Linux packages. Everything is in the root `installer/` folder and `installer/scripts/build.py`.

## What is built

| Where | What you get | Built with |
| --- | --- | --- |
| Windows | `example-cli-<version>-setup.exe` (with an uninstaller and an optional PATH entry) and a portable zip `example-cli-<cli version>-windows-x64.zip` | PyInstaller and NSIS |
| Linux | the command line as `.deb` and `.rpm`, for x86_64 and arm64 | PyInstaller and nfpm |
| macOS | no installer: install the PyPI package (`uv tool install example-cli`) | |

## Versions

The setup has its own version (`version` in `installer/build.toml`, history in [`installer/CHANGELOG.md`](../CHANGELOG.md)), tagged `installer-v<version>`. It is separate from the command line it contains, so an installer-only fix can ship without touching the command line.

- Raise the setup version whenever the command line or the installer changes, by at least as much as the biggest change inside.
- Each setup records the command line's version in the registry (`CliVersion`).
- The zip and the Linux packages carry the command line's own version.

## The files

```text
installer/
  build.toml                the setup's version, title, publisher, install folder and what is frozen
  CHANGELOG.md              the installers' history
  pyinstaller/cli.spec      freezes the command line into one folder
  windows/setup.nsi         the Windows setup and uninstaller
  windows/path.ps1          the PATH edit, run by the setup
  linux/nfpm.yaml           the deb and rpm packages
  tools.toml                pinned NSIS and nfpm versions
  scripts/build.py          the build: names and versions, PyInstaller helpers, NSIS, the zip, nfpm,
                            signing and branding
brand/                      sample icon and setup artwork (see brand/README.md)
```

Names, version and description are never repeated. The executable name is the `[project.scripts]` key of `packages/cli/pyproject.toml`, and the version is `__version__` in `example_cli/__init__.py`; `build.toml` says where to read each. Renaming the command needs no edit in the installer beyond `build.toml`.

## Building the installers

```bash
uv sync --group installer
uv run python installer/scripts/build.py --smoke                  # the formats this OS builds
uv run python installer/scripts/build.py --format deb,rpm --smoke # Linux: the packages
```

`--sync` runs `uv sync` for the installer group first. `--smoke` starts the built program and checks it answers (`packages/cli/tests/integration/test_frozen_cli.py`). A format the current OS cannot build (`deb` or `rpm` on Windows, `exe` on Linux) stops the build with an error. Results are in `dist/installer/` and the PyInstaller folder is in `build/installer/`.

| You need | For |
| --- | --- |
| `uv sync --group installer` | PyInstaller and the build backend |
| NSIS (version in `installer/tools.toml`) | the Windows setup; `makensis` on `PATH` or in `Program Files (x86)\NSIS` |
| nfpm (version in `installer/tools.toml`) | the Linux packages; set `NFPM` to run it another way, for example `NFPM="uvx nfpm"` |

### PyInstaller

`cli.spec` makes a one-folder build (no one-file build): `example-cli(.exe)` and one `lib/` folder with the Python runtime and the dependencies. The entry script is generated from the `[project.scripts]` target, and the Windows executable carries the icon and file properties taken from the project. `collect` and `compile-pyc` in `build.toml` list libraries that are frozen whole, or shipped as compiled `.pyc` files.

### Windows setup

The setup installs for the current user by default (all users asks for administrator rights), offers to add the install folder to `PATH`, and creates a Start Menu folder with an uninstaller and a prompt where the command already works.

```text
Setup.exe /S [/allusers | /currentuser] [/NOPATH] [/D=C:\folder]
uninstall.exe /S
```

### Linux packages

The folder is installed under `/usr/lib/example-cli/`, the command is a symlink in `/usr/bin`, and the icon is installed in the `hicolor` theme. Packages are system-wide and nothing in a user's home folder is ever touched.

### Signing

Signing is off by default. Set the repository variable `SIGN_COMMAND` to a command that signs one file, with `{file}` where its path goes; the executable and then the setup are signed.

## Releasing

Publish a GitHub release tagged `installer-v<version>`. The `Release installer` workflow checks the tag against `installer/build.toml`, builds the Windows files and the Linux packages (x86_64 and arm64), and after the approval of the `installer` environment attaches them, with `SHA256SUMS.txt`, to the release. Nothing goes to PyPI. The `installer-latest` tag and pre-release then move to the new version.
