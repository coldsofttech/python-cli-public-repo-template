#!/usr/bin/env python3
"""Build the installers: a Windows setup and zip of the command line, and its Linux packages.

    uv sync --group installer
    uv run python installer/scripts/build.py [--sync] [--smoke] [--format exe,deb,rpm]

On Windows it writes example-cli-<version>-setup.exe and the command line's portable zip. On Linux
it writes the command line's deb and rpm. Everything comes from the package's own metadata (its
pyproject.toml and installer/build.toml), so renaming the command needs no edit here. Icon and
setup art are named in installer/build.toml. Tool versions are pinned in installer/tools.toml. The
installers are written to dist/installer/. See installer/docs/packaging.md.

Signing is off by default. Set SIGN_COMMAND to a command that signs one file, with {file} where
its path goes (for example a signtool or SignPath call); the executable and then the setup.exe
are signed. Nothing in this script is tied to one provider.
"""

import argparse
import functools
import importlib.util
import os
import platform
import re
import shlex
import shutil
import stat
import subprocess
import sys
import tomllib
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, TypeVar

ROOT = Path(__file__).resolve().parents[2]
INSTALLER = ROOT / "installer"
BUILD = ROOT / "build" / "installer"
WORK = ROOT / "build" / "installer-work"
OUT = ROOT / "dist" / "installer"
WINDOWS = sys.platform == "win32"
LINUX = sys.platform.startswith("linux")
T = TypeVar("T")


@functools.cache
def build_settings() -> dict[str, Any]:
    """installer/build.toml: the setup's version, names and artwork."""
    return tomllib.loads((INSTALLER / "build.toml").read_text(encoding="utf-8"))


# ---- the program: names and versions from pyproject.toml, and what PyInstaller freezes ---------
class Collected:
    """Data files, native libraries and hidden imports gathered for one executable."""

    def __init__(self) -> None:
        self.datas: list[Any] = []
        self.binaries: list[Any] = []
        self.hiddenimports: list[str] = []

    def package(self, name: str) -> None:
        """Collect a package whole: code, data files, native libraries and submodules."""
        from PyInstaller.utils.hooks import collect_all

        if importlib.util.find_spec(name) is None:
            return
        datas, binaries, hidden = collect_all(name)
        self.datas.extend(datas)
        self.binaries.extend(binaries)
        self.hiddenimports.extend(hidden)

    def metadata(self, *distributions: str) -> None:
        """Keep the package metadata that ``importlib.metadata`` reads at run time."""
        from PyInstaller.utils.hooks import copy_metadata

        for distribution in distributions:
            self.datas.extend(copy_metadata(distribution))


class Cli:
    """The command line: its ``[cli]`` table in build.toml and its pyproject.toml.

    Renaming the command needs no edit here: the executable is the one key of
    ``[project.scripts]``.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.directory = ROOT / config["path"]
        pyproject = self.directory / "pyproject.toml"
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        self.project: dict[str, Any] = data["project"]
        scripts: dict[str, str] = self.project.get("scripts", {})
        if len(scripts) != 1:
            raise SystemExit(f"{pyproject} needs exactly one [project.scripts] entry.")
        ((self.script, self.entry_point),) = scripts.items()
        self.module = self.entry_point.split(":")[0]
        self.package = self.module.split(".")[0]
        self.core_package: str = config["core-package"]
        self.excludes: list[str] = config.get("excludes", [])
        self.collect: list[str] = config.get("collect", [])
        self.compile_pyc: list[str] = config.get("compile-pyc", [])
        self.smoke: str | None = config.get("smoke")
        self.title = self.resolve("title")
        self.version = self.resolve("version", "pyproject")

    def resolve(self, key: str, default: str | None = None) -> str:
        """A value kept in the code: a literal, ``"pyproject"`` (``[project] version``), or a
        ``{file, pattern}`` table (a file of the package and a regex whose first group is it)."""
        value = self.config.get(key, default)
        if value is None:
            raise SystemExit(f"[cli] in build.toml needs {key}.")
        if isinstance(value, str):
            return str(self.project[key]) if value == "pyproject" else value
        path = self.directory / value["file"]
        match = re.search(value["pattern"], path.read_text(encoding="utf-8"), re.MULTILINE)
        if not match:
            raise SystemExit(f"{key} of [cli] not found in {path}")
        return match.group(1)

    def values(self) -> dict[str, str]:
        """The names the CI steps need, as environment variables."""
        return {
            "CLI_NAME": self.script,
            "CLI_MODULE": self.module,
            "CLI_PACKAGE": self.package,
            "CORE_PACKAGE": self.core_package,
            "APP_VERSION": self.version,
            "APP_TITLE": self.title,
        }

    def dependencies(self) -> Collected:
        """What the program needs frozen in."""
        from PyInstaller.utils.hooks import collect_submodules

        collected = Collected()
        collected.metadata(self.project["name"])
        collected.hiddenimports.extend(collect_submodules(self.core_package))
        collected.hiddenimports.extend(collect_submodules(self.package))
        for package in self.collect:
            collected.package(package)
        return collected

    def compile_sources(self, datas: list[Any]) -> list[Any]:
        """Ship the ``.py`` data files of the ``compile-pyc`` folders as compiled ``.pyc`` files.

        The folders are paths under ``lib/``. A ``.pyc`` next to where its source was is imported
        without the source. It is compiled with the Python that runs the build, which is the one
        that is frozen, and does not check the source's timestamp. The source's path is replaced
        by the file's place in ``lib/``, so tracebacks do not show the build machine's folders.
        """
        if not self.compile_pyc:
            return datas
        import py_compile

        from PyInstaller.config import CONF

        folders = tuple(f"{folder.strip('/')}/" for folder in self.compile_pyc)
        out = Path(CONF["workpath"]) / "pyc"
        converted: list[Any] = []
        for entry in datas:
            dest = entry[0].replace("\\", "/")
            if not (dest.endswith(".py") and dest.startswith(folders)):
                converted.append(entry)
                continue
            target = out / f"{dest}c"
            target.parent.mkdir(parents=True, exist_ok=True)
            py_compile.compile(
                entry[1],
                cfile=str(target),
                dfile=dest,
                doraise=True,
                invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH,
            )
            converted.append((f"{dest}c", str(target), entry[2]))
        return converted

    def entry_script(self) -> str:
        """Write the small script PyInstaller freezes for the program's entry point."""
        from PyInstaller.config import CONF

        function = self.entry_point.split(":")[1]
        path = Path(CONF["workpath"]) / f"entry_{self.script}.py"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "import multiprocessing\n"
            f"from {self.module} import {function}\n\n"
            'if __name__ == "__main__":\n'
            "    multiprocessing.freeze_support()\n"
            f"    raise SystemExit({function}())\n",
            encoding="utf-8",
        )
        return str(path)

    def version_info(self) -> Any:
        """Windows file properties (Explorer > Properties > Details) from build.toml."""
        from PyInstaller.utils.win32.versioninfo import (
            FixedFileInfo,
            StringFileInfo,
            StringStruct,
            StringTable,
            VarFileInfo,
            VarStruct,
            VSVersionInfo,
        )

        numbers = [int(n) for n in re.findall(r"\d+", self.version)[:4]]
        version = tuple(numbers + [0] * (4 - len(numbers)))
        settings = build_settings()
        publisher = settings["publisher"]
        strings = {
            "CompanyName": publisher,
            "FileDescription": self.project.get("description", self.title),
            "FileVersion": self.version,
            "ProductName": self.title,
            "ProductVersion": self.version,
            "LegalCopyright": f"{settings['licence']['name']}. {publisher}",
        }
        return VSVersionInfo(
            ffi=FixedFileInfo(
                filevers=version,
                prodvers=version,
                mask=0x3F,
                flags=0x0,
                OS=0x40004,
                fileType=0x1,
                subtype=0x0,
                date=(0, 0),
            ),
            kids=[
                StringFileInfo(
                    [StringTable("040904B0", [StringStruct(k, v) for k, v in strings.items()])]
                ),
                VarFileInfo([VarStruct("Translation", [1033, 1200])]),
            ],
        )

    def program(self) -> tuple[Any, Any]:
        """Analyse the program and describe its executable: ``(Analysis, EXE)`` for the spec."""
        from PyInstaller.building.api import EXE, PYZ
        from PyInstaller.building.build_main import Analysis

        collected = self.dependencies()
        analysis = Analysis(
            [self.entry_script()],
            pathex=[str(self.directory / "src")],
            binaries=collected.binaries,
            datas=collected.datas,
            hiddenimports=collected.hiddenimports,
            hookspath=[],
            hooksconfig={},
            runtime_hooks=[],
            excludes=self.excludes,
            noarchive=False,
        )
        analysis.datas = self.compile_sources(analysis.datas)
        exe = EXE(
            PYZ(analysis.pure),
            analysis.scripts,
            [],
            exclude_binaries=True,
            name=self.script,
            console=True,
            icon=str(brand_icon()) if WINDOWS else None,
            version=self.version_info() if WINDOWS else None,
            upx=False,
            # Everything but the executable goes in lib/ (COLLECT follows the EXE).
            contents_directory="lib",
        )
        return analysis, exe


def load_cli() -> Cli:
    """The ``[cli]`` table of build.toml."""
    return Cli(build_settings()["cli"])


def github_env() -> None:
    """Print the project names and, on GitHub, add them to ``GITHUB_ENV`` for the later steps."""
    lines = "".join(f"{key}={value}\n" for key, value in load_cli().values().items())
    if "GITHUB_ENV" in os.environ:
        with open(os.environ["GITHUB_ENV"], "a", encoding="utf-8") as env:
            env.write(lines)
    sys.stdout.write(lines)


def run(command: list[str], *, env: dict[str, str] | None = None, cwd: Path = ROOT) -> None:
    print("+", " ".join(shlex.quote(part) for part in command), flush=True)
    subprocess.run(command, check=True, cwd=cwd, env=env)


def run_parallel(tasks: list[Callable[[], T]], jobs: int) -> list[T]:
    """Run independent ``tasks`` on up to ``jobs`` threads; results keep the order of ``tasks``.

    The work is in subprocesses (nfpm), so threads are enough. The first failure is raised once
    the others have finished.
    """
    with ThreadPoolExecutor(max_workers=max(1, min(jobs, len(tasks) or 1))) as pool:
        futures = [pool.submit(task) for task in tasks]
        return [future.result() for future in futures]


# ---- PyInstaller -------------------------------------------------------------------------------
def freeze() -> Path:
    """Run PyInstaller on the spec and return its output folder."""
    run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            str(build_file("spec")),
            "--noconfirm",
            "--distpath",
            str(BUILD),
            "--workpath",
            str(WORK / "pyinstaller"),
        ]
    )
    return BUILD / build_settings()["name"]


# ---- branding: the artwork named under [brand] in installer/build.toml ----------------------
def configured(section: str, key: str) -> Path | None:
    """The file or folder named by ``[<section>] <key>`` (from the repository root), if any."""
    value = build_settings().get(section, {}).get(key)
    if value is None:
        return None
    path = ROOT / value
    if not path.exists():
        raise SystemExit(f"[{section}] {key} in build.toml names {value}, which is missing.")
    return path


def build_formats() -> tuple[list[str], list[str]]:
    """The formats of ``[formats]`` in build.toml: the ones this OS builds, and all of them."""
    table: dict[str, list[str]] = build_settings().get("formats", {})
    here = table.get("windows" if WINDOWS else "linux", [])
    return list(here), sorted({name for names in table.values() for name in names})


def build_file(key: str, section: str = "build") -> Path:
    """A required file named under ``[build]`` (``spec``, ``nsi``, ``nfpm``) or another section."""
    path = configured(section, key)
    if path is None:
        raise SystemExit(f"installer/build.toml needs [{section}] {key}.")
    return path


@functools.cache
def brand_icon() -> Path:
    """The icon of the executable, the setup and the uninstaller: ``[brand] icon`` (.ico)."""
    icon = configured("brand", "icon")
    if icon is None:
        raise SystemExit("installer/build.toml needs [brand] icon.")
    return icon


def brand_art() -> dict[str, str]:
    """The setup's header and welcome bitmaps, when ``[brand]`` names them (NSIS has defaults)."""
    names = {"HEADER_IMAGE": "header-image", "WELCOME_IMAGE": "welcome-image"}
    return {
        flag: str(path)
        for flag, key in names.items()
        if (path := configured("brand", key)) is not None
    }


def brand_png_dir() -> Path:
    """The folder with the package icons (app-16.png ... app-256.png): ``[brand] png-dir``."""
    folder = configured("brand", "png-dir")
    if folder is None or not sorted(folder.glob("app-*.png")):
        raise SystemExit("installer/build.toml needs [brand] png-dir, a folder with app-*.png.")
    return folder


# ---- Windows: NSIS and zip ---------------------------------------------------------------------
def sign(files: list[Path]) -> None:
    """Sign ``files`` with SIGN_COMMAND, if it is set; otherwise do nothing."""
    template = os.environ.get("SIGN_COMMAND", "").strip()
    if not template:
        return
    if "{file}" not in template:
        raise SystemExit("SIGN_COMMAND must contain {file}, where the file to sign goes.")
    for file in files:
        command = template.replace("{file}", f'"{file}"')
        print("+", command, flush=True)
        # Windows takes the command line as written; elsewhere it is split like a shell would.
        # SIGN_COMMAND is set by whoever runs the build (a CI variable), so it is trusted input.
        subprocess.run(command if WINDOWS else shlex.split(command), check=True, cwd=ROOT)


def find_makensis() -> str:
    found = shutil.which("makensis")
    if found:
        return found
    for variable in ("ProgramFiles(x86)", "ProgramFiles"):
        candidate = Path(os.environ.get(variable, "")) / "NSIS" / "makensis.exe"
        if candidate.is_file():
            return str(candidate)
    raise SystemExit("makensis not found. Install NSIS (version in installer/tools.toml).")


def numeric_version(version: str) -> str:
    numbers = re.findall(r"\d+", version)[:4]
    return ".".join(numbers + ["0"] * (4 - len(numbers)))


def package_exe(cli: Cli, folder: Path) -> Path:
    """Build the NSIS setup."""
    OUT.mkdir(parents=True, exist_ok=True)
    sign(sorted(folder.glob("*.exe")))
    settings = build_settings()
    setup = OUT / f"{settings['name']}-{settings['version']}-setup.exe"
    links = settings.get("links", {})
    flags = {
        "GUID": settings["guid"],
        "APP_NAME": settings["title"],
        "APP_VERSION": settings["version"],
        "APP_VERSION_NUMERIC": numeric_version(settings["version"]),
        "STAGE_DIR": str(folder),
        "CLI_EXE": f"{cli.script}.exe",
        "CLI_VERSION": cli.version,
        "OUT_FILE": str(setup),
        "ICON_FILE": str(brand_icon()),
        **brand_art(),
        "LICENSE_FILE": str(build_file("file", "licence")),
        "PUBLISHER": settings["publisher"],
        "INSTALL_DIR": settings["install-dir"].replace("/", "\\"),
        "INSTALL_DIR_DEPTH": len(settings["install-dir"].split("/")),
        "START_MENU_DIR": settings["start-menu-dir"].replace("/", "\\"),
        "START_MENU_DIR_DEPTH": len(settings["start-menu-dir"].split("/")),
        "SUPPORT_URL": str(links.get("issues", "")),
        "UPDATE_URL": str(links.get("changelog", "")),
        "URL": str(links.get("homepage", "")),
    }
    command = [find_makensis(), "/V2"]
    command += [f"/D{key}={value}" for key, value in flags.items() if value]
    run([*command, str(build_file("nsi"))])
    sign([setup])
    return setup


def package_zip(cli: Cli, folder: Path) -> Path:
    """The command line as a portable zip (what a Scoop manifest installs)."""
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / f"{build_settings()['name']}-{cli.version}-windows-x64"
    return Path(shutil.make_archive(str(target), "zip", root_dir=folder))


# ---- Linux -------------------------------------------------------------------------------------
def normalise_modes(folder: Path) -> None:
    """Folders 755, files 644, and 755 for anything executable, whatever the build umask was."""
    for path in [folder, *folder.rglob("*")]:
        if path.is_symlink():
            continue
        if path.is_dir() or path.stat().st_mode & stat.S_IXUSR or ".so" in path.name:
            path.chmod(0o755)
        else:
            path.chmod(0o644)


def package_linux(cli: Cli, folder: Path, formats: list[str], jobs: int) -> list[Path]:
    """Build the deb and rpm packages of the command line."""
    normalise_modes(folder)
    OUT.mkdir(parents=True, exist_ok=True)
    machine = platform.machine().lower()
    authors = cli.project.get("authors") or [{}]
    maintainer = authors[0].get("name", "")
    if authors[0].get("email"):
        maintainer = f"{maintainer} <{authors[0]['email']}>"
    links = build_settings().get("links", {})
    env = {
        **os.environ,
        "PKG_NAME": cli.script,
        "PKG_VERSION": cli.version,
        "PKG_ARCH": {"x86_64": "amd64", "amd64": "amd64", "aarch64": "arm64"}.get(machine, machine),
        "PKG_DESCRIPTION": str(cli.project.get("description", cli.script)),
        "PKG_MAINTAINER": maintainer,
        "PKG_HOMEPAGE": str(links.get("homepage", "")),
        "PKG_LICENSE": str(cli.project.get("license", "")),
        "PKG_SOURCE_DIR": str(folder),
        "PKG_LICENSE_FILE": str(build_file("file", "licence")),
        "PKG_ICON_DIR": str(brand_png_dir()),
    }
    nfpm = shlex.split(os.environ.get("NFPM", "nfpm"))
    if shutil.which(nfpm[0]) is None:
        raise SystemExit(
            "nfpm not found. Install it (version in installer/tools.toml) or set NFPM."
        )
    before = set(OUT.iterdir())

    def package(packager: str) -> None:
        run(
            [*nfpm, "package", "--config", str(build_file("nfpm")),
             "--packager", packager, "--target", str(OUT)],
            env=env,
        )  # fmt: skip

    run_parallel([functools.partial(package, packager) for packager in formats], jobs)
    return sorted(set(OUT.iterdir()) - before)


# ---- driver ------------------------------------------------------------------------------------
def sync() -> None:
    """Install the command line and the installer dependency group, and nothing else."""
    uv = shutil.which("uv")
    if uv is None:
        raise SystemExit("--sync needs uv on PATH.")
    run([uv, "sync", "--package", load_cli().project["name"], "--group", "installer", "--no-dev"])


def smoke(cli: Cli) -> None:
    """Start the built program and check it answers: the ``smoke`` test of the command line."""
    if cli.smoke:
        run(
            [sys.executable, "-m", "pytest", *build_settings()["build"]["smoke-args"], cli.smoke],
            cwd=cli.directory,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the installers.")
    parser.add_argument("--sync", action="store_true", help="uv sync the installer group first")
    parser.add_argument("--smoke", action="store_true", help="run the smoke test on the build")
    parser.add_argument("--github-env", action="store_true",
                        help="add the project names to GITHUB_ENV, print them, stop")  # fmt: skip
    allowed, known = build_formats()
    parser.add_argument(
        "--format",
        metavar="exe,deb,rpm",
        help=f"comma-separated formats, here: {', '.join(allowed)} (default: all)",
    )
    parser.add_argument("--jobs", type=int, default=os.cpu_count() or 1,
                        help="builds to run at once (1 = one after the other)")  # fmt: skip
    args = parser.parse_args()

    if args.github_env:
        github_env()
        return
    if not (WINDOWS or LINUX):
        raise SystemExit("Installers are built on Windows (setup.exe) and Linux (deb, rpm) only.")
    formats = [f.strip() for f in args.format.split(",") if f.strip()] if args.format else []
    unknown = sorted(set(formats) - set(known))
    if unknown:
        parser.error(f"unknown format: {', '.join(unknown)} (choose from {', '.join(known)})")
    wrong = [f for f in formats if f not in allowed]
    if wrong:
        raise SystemExit(
            f"--format {','.join(wrong)} cannot be built on this OS (here: {', '.join(allowed)})."
        )
    formats = formats or allowed

    if args.sync:
        sync()
    cli = load_cli()
    if WINDOWS:
        brand_icon()  # fail early, before the build
    folder = freeze()
    if WINDOWS:
        built = [package_exe(cli, folder), package_zip(cli, folder)]
    else:
        built = package_linux(cli, folder, formats, args.jobs)
    if args.smoke:
        smoke(cli)
    print("\nBuilt:")
    for path in built:
        print(f"  {path.relative_to(ROOT)}  ({path.stat().st_size / 1_048_576:.1f} MB)")


if __name__ == "__main__":
    main()
