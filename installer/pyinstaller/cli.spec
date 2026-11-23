# PyInstaller spec for the command line: one executable and its lib/ folder, any OS.
#
#   example-cli(.exe)   the command line (console)
#   lib/                the Python runtime and the command line's dependencies
#
# One-folder build on purpose (no one-file build). Names, version, icon and dependencies: see the
# Cli class in installer/scripts/build.py and installer/build.toml.
#   uv sync --group installer
#   uv run python installer/scripts/build.py

import sys
from pathlib import Path

sys.path.insert(0, str(Path(SPECPATH).parent / "scripts"))
import build  # noqa: E402

analysis, exe = build.load_cli().program()

coll = COLLECT(exe, analysis.binaries, analysis.datas, name=build.build_settings()["name"], upx=False)
