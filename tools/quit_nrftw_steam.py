#!/usr/bin/env python3
"""Ask Windows Steam in a Sikarugir game wrapper to exit cleanly."""

import argparse
import os
from pathlib import Path
import subprocess
import sys
import time


def processes() -> list[str]:
    try:
        output = subprocess.check_output(
            ["ps", "-axo", "comm="], text=True, stderr=subprocess.DEVNULL
        )
    except (OSError, subprocess.CalledProcessError):
        raise SystemExit("Cannot check running processes; Steam was not touched")
    return output.splitlines()


def is_steam(line: str) -> bool:
    # Wine reports the path as launched: Steam.exe or steam.exe.
    return line.strip().lower().endswith("\\steam\\steam.exe")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--app",
        type=Path,
        default=Path.home() / "Games/No Rest for the Wicked (Wine).app",
        help="path to the tested Sikarugir wrapper",
    )
    args = parser.parse_args()
    app = args.app.expanduser().resolve()
    wine = app / "Contents/SharedSupport/wine/bin/wine"
    prefix = app / "Contents/SharedSupport/prefix"
    steam = prefix / "drive_c/Program Files (x86)/Steam/Steam.exe"
    if not wine.is_file() or not steam.is_file():
        raise SystemExit("Wine or Windows Steam is missing from this wrapper")

    running = processes()
    if any("\\steamapps\\common\\" in line.lower() for line in running):
        raise SystemExit("A game is running. Exit it and wait for Steam Cloud first")
    if not any(is_steam(line) for line in running):
        print("Steam is already stopped")
        return 0

    support = app / "Contents/SharedSupport"
    frameworks = app / "Contents/Frameworks"
    library_paths = [
        frameworks / "moltenvkcx",
        support / "wine/lib",
        support / "wine/lib64",
        frameworks,
        frameworks / "GStreamer.framework/Libraries",
    ]
    env = os.environ.copy()
    env.update(
        WINEPREFIX=str(prefix),
        WINEDEBUG="-all",
        WINEMSYNC="1",
        WINEESYNC="1",
        DYLD_FALLBACK_LIBRARY_PATH=":".join(map(str, library_paths))
        + ":/opt/wine/lib:/usr/lib:/usr/libexec:/usr/lib/system",
    )
    result = subprocess.run(
        [str(wine), r"C:\Program Files (x86)\Steam\Steam.exe", "-shutdown"],
        env=env,
        check=False,
    )
    if result.returncode:
        print("Steam shutdown command failed", file=sys.stderr)
        return result.returncode
    for _ in range(20):
        if not any(is_steam(line) for line in processes()):
            print("Steam stopped")
            return 0
        time.sleep(1)
    print("Steam is still running; check its window for a pending dialog", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
