"""
Cross-platform build script for the PySide6 app using PyInstaller.
- Prefers an existing spec file (BASIL.spec).
- Falls back to building from main.py with sensible defaults.

Usage:
    python build.py            # normal build
    python build.py --clean    # clean PyInstaller cache and dist/build dirs before building
    python build.py --onefile  # build a single-file executable (slower startup)
    python build.py --name BASIL  # override app name
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SPEC_FILE = ROOT / "BASIL.spec"
ENTRY = ROOT / "main.py"
DIST = ROOT / "dist"
BUILD = ROOT / "build"
DEFAULT_NAME = "BASIL"


def run(cmd: list[str]) -> int:
    print("\n> ", " ".join(cmd))
    return subprocess.call(cmd)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the PySide6 app with PyInstaller")
    parser.add_argument("--clean", action="store_true", help="Clean previous builds and cache")
    parser.add_argument("--onefile", action="store_true", help="Build as a single-file executable")
    parser.add_argument("--name", default=DEFAULT_NAME, help="Application name")
    args = parser.parse_args()

    if args.clean:
        for p in (DIST, BUILD, ROOT / "__pycache__"):
            if p.exists():
                print(f"Removing {p}")
                shutil.rmtree(p, ignore_errors=True)
        pycache = ROOT / ".pyinstaller"
        if pycache.exists():
            print(f"Removing {pycache}")
            shutil.rmtree(pycache, ignore_errors=True)

    pyinstaller_cmd = [sys.executable, "-m", "PyInstaller"]

    if SPEC_FILE.exists():
        # provided spec for consistent packaging
        cmd = pyinstaller_cmd + [str(SPEC_FILE)]
    else:
        # Fallback sensible defaults for a windowed PySide6 app
        if not ENTRY.exists():
            print("Error: main.py not found and no main.spec present.")
            return 1
        cmd = pyinstaller_cmd + [
            "--name",
            args.name,
            "--noconfirm",
            "--clean",
            "--windowed",
            # excludes to keep size down
            "--exclude-module",
            "tkinter",
            "--exclude-module",
            "pytest",
            "--exclude-module",
            "unittest",
            "--exclude-module",
            "curses",
            "--exclude-module",
            "pydoc",
            "--exclude-module",
            "pydoc_data",
            "--exclude-module",
            "doctest",
            "--exclude-module",
            "email",
            "--exclude-module",
            "http",
            "--exclude-module",
            "xml",
            "--exclude-module",
            "sqlite3",
            "--exclude-module",
            "asyncio",
            "--exclude-module",
            "multiprocessing",
            "--exclude-module",
            "subprocess",
            "--exclude-module",
            "threading",
            "--exclude-module",
            "zoneinfo",

        ]
        if args.onefile:
            cmd.append("--onefile")
        cmd.append(str(ENTRY))

    return run(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
