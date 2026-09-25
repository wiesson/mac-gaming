#!/usr/bin/env python3
"""List, validate, and inspect local mac-gaming profiles (read-only)."""

from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path
import plistlib
import re
import shutil
import subprocess
import sys

from configure_nrftw import device_settings, steam_values


ROOT = Path(__file__).resolve().parent.parent
PROFILES = ROOT / "profiles"
GAME_LAUNCH = re.compile(
    r'^\[([^]]+)\] AppID 1371980 adding PID (\d+) as a tracked process .*NoRestForTheWicked\.exe'
)
GAME_EXIT = re.compile(
    r'^\[([^]]+)\] AppID 1371980 no longer tracking PID (\d+), exit code (-?\d+)'
)
CLOUD_UPLOAD = re.compile(
    r'^\[([^]]+)\] \[AppID 1371980\] Upload complete, result OK'
)


def recent_game_exits(log: str, count: int = 3) -> list[tuple[str, int]]:
    game_pids = set()
    exits = []
    for line in log.splitlines():
        if match := GAME_LAUNCH.search(line):
            game_pids.add(match.group(2))
        elif (match := GAME_EXIT.search(line)) and match.group(2) in game_pids:
            exits.append((match.group(1), int(match.group(3))))
            game_pids.remove(match.group(2))
    return exits[-count:]


def latest_cloud_upload(log: str) -> str | None:
    matches = [match.group(1) for line in log.splitlines() if (match := CLOUD_UPLOAD.search(line))]
    return matches[-1] if matches else None


def load_profiles() -> dict[str, dict]:
    result = {}
    for path in sorted(PROFILES.glob("*/profile.json")):
        data = json.loads(path.read_text())
        if data.get("schema_version") != 1:
            raise ValueError(f"{path}: unsupported schema_version")
        if data.get("slug") != path.parent.name:
            raise ValueError(f"{path}: slug must match its directory")
        if not isinstance(data.get("name"), str) or not data["name"]:
            raise ValueError(f"{path}: missing name")
        if data.get("runner", {}).get("kind") not in {"sikarugir", "custom-wine"}:
            raise ValueError(f"{path}: unsupported runner kind")
        if not (path.parent / "README.md").is_file():
            raise ValueError(f"{path}: missing README.md")
        result[data["slug"]] = data
    if not result:
        raise ValueError("No profiles found")
    return result


def doctor_nrf(profile: dict, games_dir: Path) -> None:
    app = games_dir / profile["runner"]["app_name"]
    print("Wrapper:", app)
    if not app.is_dir():
        print("  Missing. Follow the profile setup guide.")
        return
    plist_path = app / "Contents/Info.plist"
    prefix = app / "Contents/SharedSupport/prefix"
    if not plist_path.is_file() or not prefix.is_dir():
        print("  Incomplete wrapper (Info.plist or prefix missing)")
        return
    plist = plistlib.loads(plist_path.read_bytes())
    print("  D3DMetal:", plist.get("D3DMETAL"))
    print("  MSync:", plist.get("WINEMSYNC"))
    print("  Steam target:", plist.get("Program Name and Path"))
    print("  Auto-launch:", plist.get("Program Flags"))
    version = app / "Contents/SharedSupport/wine/version"
    print("  Wine engine:", version.read_text().strip() if version.is_file() else "unknown")
    steam = prefix / "drive_c/Program Files (x86)/Steam"
    print("  Windows Steam:", "found" if (steam / "steam.exe").is_file() else "missing")
    game = steam / "steamapps/common" / profile["steam"]["install_dir"] / "NoRestForTheWicked.exe"
    print("  Game files:", "found" if game.is_file() else "missing")
    configs = sorted((steam / "userdata").glob("*/config/localconfig.vdf"))
    if len(configs) == 1:
        try:
            overlay, options = steam_values(configs[0].read_text())
            print("  Game overlay:", overlay)
            print("  Launch options:", options)
        except ValueError:
            print("  Steam game settings: not initialized")
    elif configs:
        print("  Steam game settings: multiple accounts; inspect the intended one")
    else:
        print("  Steam game settings: missing; sign in first")
    reg = prefix / "user.reg"
    settings = device_settings(reg.read_text()) if reg.is_file() else None
    print("  LockedCursor:", settings.get("LockedCursor") if settings else "not created yet")
    logs = steam / "logs"
    game_log = logs / "gameprocess_log.txt"
    if game_log.is_file():
        exits = recent_game_exits(game_log.read_text(errors="replace"))
        for date, code in exits:
            detail = " (Windows access violation)" if code == -1073741819 else ""
            print(f"  Game exit: {date}, code {code}{detail}")
        if not exits:
            print("  Game exit: none recorded")
    cloud_log = logs / "cloud_log.txt"
    if cloud_log.is_file():
        upload = latest_cloud_upload(cloud_log.read_text(errors="replace"))
        print("  Last successful Cloud upload:", upload or "none recorded")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="show available game profiles")
    sub.add_parser("validate", help="validate profile metadata and documentation")
    doctor = sub.add_parser("doctor", help="read-only inspection of one profile")
    doctor.add_argument("slug", help="profile slug")
    doctor.add_argument("--games-dir", type=Path, default=Path.home() / "Games")
    args = parser.parse_args()
    try:
        profiles = load_profiles()
    except (ValueError, json.JSONDecodeError) as error:
        print(error, file=sys.stderr)
        return 1
    if args.command == "list":
        for slug, data in profiles.items():
            print(f"{slug}: {data['name']} ({data['store']})")
        return 0
    if args.command == "validate":
        print(f"Validated {len(profiles)} profiles")
        return 0
    profile = profiles.get(args.slug)
    if not profile:
        print(f"Unknown profile: {args.slug}", file=sys.stderr)
        return 2
    print(profile["name"], "—", profile["status"])
    print("Host:", platform.system(), platform.mac_ver()[0] or platform.release(), platform.machine())
    games_dir = args.games_dir.expanduser().resolve()
    if games_dir.exists():
        free_gib = shutil.disk_usage(games_dir).free / (1024 ** 3)
        print(f"Games directory: {games_dir} ({free_gib:.1f} GiB free)")
    else:
        print("Games directory:", games_dir, "(missing)")
    if platform.system() == "Darwin" and platform.machine() == "arm64":
        rosetta = subprocess.run(["arch", "-x86_64", "/usr/bin/true"], check=False).returncode == 0
        print("Rosetta 2:", "available" if rosetta else "missing")
    if profile["runner"]["kind"] == "sikarugir":
        doctor_nrf(profile, games_dir)
    else:
        print("Custom runtime: follow", PROFILES / args.slug / "README.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
