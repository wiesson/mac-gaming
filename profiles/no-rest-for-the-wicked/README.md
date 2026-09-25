# No Rest for the Wicked profile

**Tested route:** Windows Steam inside a separate [Sikarugir](https://github.com/Sikarugir-App/Sikarugir) wrapper, Wine 10.0 revision 6, Apple's D3DMetal for Direct3D 11, and MSync. Tested on an M3 Max with macOS 27.0 on September 24, 2026. Steam sign-in, game login, several minutes of gameplay, exit code 0, and Steam Cloud upload were observed. The player said it felt very good; there is no FPS benchmark or controller result yet.

This is a **free Wine route**, independent of a CrossOver license. The game still requires your Steam license. Native macOS Steam alone does not run this Windows build.

## Sources and preflight

Use the official project and vendor URLs. `sikarugir.com` is **not** the Sikarugir project's site; the [project README](https://github.com/Sikarugir-App/Sikarugir) warns about it.

| Component | Source | SHA-256 of tested archive |
|---|---|---|
| Sikarugir wrapper template 1.0.11 | [Official release asset](https://github.com/Sikarugir-App/Wrapper/releases/download/v1.0/Template-1.0.11.tar.xz) | `9fa15479e7ff6abd99c1d07be285fb95f41fc6991586502427152b1f7d6ccb8a` |
| Sikarugir Wine engine 10.0 revision 6 | [Official release asset](https://github.com/Sikarugir-App/Engines/releases/download/v1.0/WS12WineSikarugir10.0_6.tar.xz) | `9da7ee0cbf386522f3a9906943726d9c3c125dbbd9ab120e3cde80e88d6091b2` |
| Steam for Windows | [Official Steam installer](https://cdn.akamai.steamstatic.com/client/installer/SteamSetup.exe) | Changes as Steam updates |

Check Apple Silicon, macOS, Rosetta 2, and available space. A fresh game download needs roughly 50 GB plus runtime and update headroom. On an APFS volume, cloning an existing installation with `cp -cR` initially uses far less physical space, but later updates can consume more. Keep the source installation until the new route is verified.

## Assemble a separate wrapper

These commands describe the tested layout. An agent should inspect paths and use a new destination. Do not overwrite a working app. Download both archives from the official release links above, then verify them before extraction:

```sh
shasum -a 256 Template-1.0.11.tar.xz WS12WineSikarugir10.0_6.tar.xz
tar -tf Template-1.0.11.tar.xz | head
tar -tf WS12WineSikarugir10.0_6.tar.xz | head
```

The digests must match the table. Extract the template into a temporary directory, move `Template-1.0.11.app` to the wrapper path, extract the engine into `Contents/SharedSupport/`, and rename `wswine.bundle` to `wine`. Inspect the archive paths before choosing the extraction directory. Then initialize the wrapper and run Steam's official Windows installer:

```sh
wrapper="$HOME/Games/No Rest for the Wicked (Wine).app"
"$wrapper/Contents/MacOS/Sikarugir" WSS-wineprefixcreate
"$wrapper/Contents/MacOS/Sikarugir" WSS-installer "$HOME/Downloads/SteamSetup.exe"
```

The first command creates a 64-bit Wine prefix with both `Program Files` and `Program Files (x86)`. In the Steam installer, keep the default `C:\Program Files (x86)\Steam` location. Steam may download updates before showing sign-in.

Set these `Contents/Info.plist` values in the new wrapper:

| Key | Value |
|---|---|
| `D3DMETAL` | `1` |
| `WINEMSYNC` | `1` |
| `Program Name and Path` | `/Program Files (x86)/Steam/Steam.exe` |
| `Program Flags` | `-applaunch 1371980` after the first Steam sign-in |
| `WINEDEBUG` | `-all` for ordinary play |

Use `plutil -replace` or the wrapper's configuration UI. The agent should check the actual plist after editing. The D3DMetal switch must be on before the game test.

## Install or adopt the game

Sign in to **Windows Steam in this wrapper**. The player enters credentials and makes any EULA decision. Install No Rest for the Wicked from this client's library, or clone an existing game directory and its `appmanifest_1371980.acf` into this wrapper's `Steam/steamapps/`. If using a previous Steam installation, also copy `Steamworks Shared` and `appmanifest_228980.acf` if present. Keep the source library separate; do not make both Steam clients write to one folder. Restart the new Steam client so it scans the manifests, and let it verify or update files if requested.

After sign-in, quit the game and Steam, wait for Steam Cloud to finish, then run:

```sh
python3 tools/configure_nrftw.py --app "$HOME/Games/No Rest for the Wicked (Wine).app"
python3 tools/configure_nrftw.py --app "$HOME/Games/No Rest for the Wicked (Wine).app" --apply
```

The first command only reports current state. The second backs up and sets the game-specific Steam options: `-force-d3d11 -screen-fullscreen 0 -screen-width 1280 -screen-height 720`, with Steam Overlay off. It also sets the game's `LockedCursor=false` if the game has already created its device settings in `user.reg`. If that key is not present, run the helper again after the first normal game exit. Check `Steam/userdata/<id>/config/localconfig.vdf` and `user.reg` without printing account data.

Start the wrapper. Steam should launch the game with the saved DX11 flags. In this Sikarugir profile, the Option key is mapped to Windows Alt, so try **Option + Return** for the full-screen toggle. CrossOver commonly maps Command to Windows Alt, which explains a different shortcut there. The Windows game may show a generic `wine` Dock icon; that alone is not a failure.

## Verify and tune

1. Confirm the game reaches the menu and gameplay, accepts mouse and keyboard, and has sound. Check that the cursor can leave the window after `LockedCursor=false` is applied.
2. Exit through the game menu. Run `python3 tools/mac_gaming.py doctor no-rest-for-the-wicked` to see the last three game exit codes and the last successful Steam Cloud upload. A code of `0` is a clean exit; `-1073741819` is a Windows access violation and needs investigation if it keeps recurring. The report reads the local Steam logs without printing save paths or account details.
3. For a controller, first pair it in macOS (USB or Bluetooth), then check **Steam > Settings > Controller** in this Windows Steam client and test in game. The [Steam game page](https://store.steampowered.com/app/1371980/No_Rest_for_the_Wicked/) lists Xbox and PlayStation controllers and recommends controller play. Controller passthrough in this Wine profile is not yet verified.
4. If the game feels faster than a prior setup, compare the same scene and resolution with an FPS or frame-time counter. A 1280×720 window is less demanding than a larger one; do not attribute the difference to Wine without a controlled comparison.

Steam often stays open after the game exits. Closing its window or quitting the macOS wrapper may leave the Windows Steam process running; Steam can then recreate its window. After Steam Cloud reports completion, use **Steam > Exit** inside the Windows client. If that only closes the window, run the tested graceful shutdown command from this repository:

```sh
python3 tools/quit_nrftw_steam.py
```

The helper refuses to run while the game is active and asks Steam itself to shut down; it does not kill Wine. On September 25, 2026, this stopped the persistent Steam process and it stayed stopped. Keep the tested DX11 and renderer settings until a specific problem justifies another change.
