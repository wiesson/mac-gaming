#!/usr/bin/env python3
"""Configure the tested No Rest for the Wicked Sikarugir profile.

Read-only by default. Never run --apply while this wrapper is active.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import plistlib
import re
import shutil
import subprocess
import tempfile


APP_ID = "1371980"
LAUNCH_OPTIONS = "-force-d3d11 -screen-fullscreen 0 -screen-width 1280 -screen-height 720"
DEVICE_KEY = "DeviceSettings_Key_h2764392784"


def app_block(text: str) -> tuple[int, int, str]:
    match = re.search(r'(?m)^(?P<indent>[ \t]*)"1371980"[ \t]*\r?\n[ \t]*\{', text)
    if not match:
        raise ValueError("Steam game settings block is missing; sign in and open the library first")
    depth = 1
    quoted = False
    escaped = False
    for pos in range(match.end(), len(text)):
        ch = text[pos]
        if escaped:
            escaped = False
        elif quoted and ch == "\\":
            escaped = True
        elif ch == '"':
            quoted = not quoted
        elif not quoted and ch == "{":
            depth += 1
        elif not quoted and ch == "}":
            depth -= 1
            if depth == 0:
                return match.end(), pos, match.group("indent")
    raise ValueError("Steam game settings block is incomplete")


def steam_values(text: str) -> tuple[str | None, str | None]:
    start, end, _ = app_block(text)
    block = text[start:end]
    def value(key: str) -> str | None:
        match = re.search(rf'(?m)^[ \t]*"{key}"[ \t]*"([^"\r\n]*)"', block)
        return match.group(1) if match else None
    return value("EnableGameOverlay"), value("LaunchOptions")


def set_steam_values(text: str) -> str:
    start, end, indent = app_block(text)
    block = text[start:end]
    newline = "\r\n" if "\r\n" in text else "\n"
    block = re.sub(
        r'(?m)^[ \t]*"(?:EnableGameOverlay|LaunchOptions)"[ \t]*"[^"\r\n]*"[^\r\n]*(?:\r?\n)?',
        "",
        block,
    )
    child_indent = indent + "\t"
    updated = (
        newline
        + child_indent + '"EnableGameOverlay"\t\t"0"' + newline
        + child_indent + '"LaunchOptions"\t\t"' + LAUNCH_OPTIONS + '"' + newline
        + block.lstrip("\r\n")
    )
    return text[:start] + updated + text[end:]


def device_match(text: str) -> re.Match[str] | None:
    return re.search(
        rf'(?m)^"{DEVICE_KEY}"=hex:([0-9a-f, \t\\\n]+)', text
    )


def device_settings(text: str) -> dict | None:
    match = device_match(text)
    if not match:
        return None
    raw = bytes.fromhex(re.sub(r'[,\s\\]', "", match.group(1))).rstrip(b"\0")
    return json.loads(raw)


def set_cursor_unlocked(text: str) -> str:
    match = device_match(text)
    if not match:
        return text
    settings = device_settings(text)
    assert settings is not None
    if settings.get("LockedCursor") is False:
        return text
    settings["LockedCursor"] = False
    encoded = ",".join(
        f"{byte:02x}"
        for byte in json.dumps(settings, separators=(",", ":")).encode() + b"\0"
    )
    return text[: match.start()] + f'"{DEVICE_KEY}"=hex:{encoded}\n' + text[match.end() :]


def save_with_backup(path: Path, content: bytes) -> bool:
    if path.read_bytes() == content:
        return False
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = path.with_name(path.name + ".bak-" + stamp)
    shutil.copy2(path, backup)
    backup.chmod(0o600)
    mode = path.stat().st_mode & 0o777
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temporary:
        temporary.write(content)
        temp_path = Path(temporary.name)
    try:
        temp_path.chmod(mode)
        os.replace(temp_path, path)
    finally:
        temp_path.unlink(missing_ok=True)
    return True


def ensure_stopped(app: Path) -> None:
    try:
        output = subprocess.check_output(
            ["ps", "-axo", "pid=,command="], text=True, stderr=subprocess.DEVNULL
        )
    except (OSError, subprocess.CalledProcessError):
        raise SystemExit("Cannot verify that Wine is stopped; --apply was not run")
    markers = (
        str(app / "Contents/MacOS/Sikarugir"),
        str(app / "Contents/SharedSupport/wine"),
    )
    if any(any(marker in line for marker in markers) for line in output.splitlines()):
        raise SystemExit("This wrapper is running. Exit the game, wait for Steam Cloud, then quit Steam before --apply.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", type=Path, required=True, help="Sikarugir game .app path")
    parser.add_argument("--steam-user", help="Steam userdata directory name if several accounts exist")
    parser.add_argument("--apply", action="store_true", help="Back up and write the tested settings")
    args = parser.parse_args()
    app = args.app.expanduser().resolve()
    plist_path = app / "Contents/Info.plist"
    prefix = app / "Contents/SharedSupport/prefix"
    if not plist_path.is_file() or not prefix.is_dir():
        raise SystemExit("Expected an initialized Sikarugir .app with an Info.plist and prefix")
    steam = prefix / "drive_c/Program Files (x86)/Steam"
    candidates = sorted((steam / "userdata").glob("*/config/localconfig.vdf"))
    if args.steam_user:
        candidates = [p for p in candidates if p.parent.parent.name == args.steam_user]
    if len(candidates) > 1:
        raise SystemExit("Several Steam accounts found; select one with --steam-user")
    config_path = candidates[0] if candidates else None
    reg_path = prefix / "user.reg"
    plist = plistlib.loads(plist_path.read_bytes())
    print("Wrapper:", app)
    print("D3DMetal:", plist.get("D3DMETAL"), "MSync:", plist.get("WINEMSYNC"))
    print("Steam auto-launch:", plist.get("Program Flags"))
    if config_path:
        original_config = config_path.read_text()
        try:
            overlay, options = steam_values(original_config)
        except ValueError as error:
            print("Steam game settings:", error)
            original_config = None
        else:
            print("Game overlay:", overlay, "Launch options:", options)
    else:
        original_config = None
        print("Steam game settings: missing (sign in first)")
    reg_text = reg_path.read_text() if reg_path.is_file() else None
    settings = device_settings(reg_text) if reg_text else None
    print("LockedCursor:", settings.get("LockedCursor") if settings else "not created yet")
    if not args.apply:
        print("Read-only check. Use --apply after quitting this wrapper.")
        return
    ensure_stopped(app)
    plist.update({
        "D3DMETAL": 1,
        "WINEMSYNC": 1,
        "Program Name and Path": "/Program Files (x86)/Steam/Steam.exe",
        "Program Flags": "-applaunch 1371980",
        "WINEDEBUG": "-all",
    })
    if save_with_backup(plist_path, plistlib.dumps(plist)):
        print("Updated wrapper configuration")
    if config_path and original_config is not None:
        updated = set_steam_values(original_config)
        if save_with_backup(config_path, updated.encode()):
            print("Updated Steam game settings")
    if reg_text and settings:
        if save_with_backup(reg_path, set_cursor_unlocked(reg_text).encode()):
            print("Unlocked game cursor")
    print("Done. Start the wrapper and verify the game.")


if __name__ == "__main__":
    main()
