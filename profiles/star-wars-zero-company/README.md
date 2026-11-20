# STAR WARS Zero Company profile

**Tested route:** Windows Steam inside a separate [Sikarugir](https://github.com/Sikarugir-App/Sikarugir) wrapper with template 1.0.27, Wine 11.0 revision 1, Apple's D3DMetal 4.0b3 for Direct3D 12, and MSync. Tested on an M3 Max with macOS 27.2.1 on November 20, 2026. Steam sign-in, the game download, and the game start were observed. The player said the game looked good and ran in borderless full screen at 3440×1440. A clean exit and a Steam Cloud upload were not yet checked. There is no FPS benchmark.

The game is an Unreal Engine 5 title that uses DirectX 12 and has no kernel anti-cheat. On Apple Silicon, DirectX 12 needs D3DMetal; DXVK and DXMT do not apply. This is a **free route** that does not need CrossOver. The game still requires your Steam license.

## Sources

Use the official GitHub release assets. `sikarugir.com` is **not** the project's site.

| Component | Source | SHA-256 |
|---|---|---|
| Sikarugir wrapper template 1.0.27 | [Release asset](https://github.com/Sikarugir-App/Template/releases/download/v1.0/Template-1.0.27.tar.xz) | `dd0778f7b553d63df9b0f4e2cda3f3c6c005aabb75588c84d604afe80cdedbb9` |
| Sikarugir Wine engine 11.0 revision 1 | [Release asset](https://github.com/Sikarugir-App/Engines/releases/download/v1.0/WS12WineSikarugir11.0_1.tar.xz) | `67e29fb3d74f363af39c69ba11f9b13a79812c5db07cf4748672658e4a200a0e` |
| Steam for Windows | [Official installer](https://cdn.akamai.steamstatic.com/client/installer/SteamSetup.exe) | Changes as Steam updates |

The digests match the ones GitHub publishes for these assets. Template 1.0.27 ships D3DMetal 4.0b3 in `Contents/SharedSupport/renderer/d3dmetal`. The download was 36.9 GB, and the installed game took 42.7 GB.

## Assemble the wrapper

The layout is the same as in the [No Rest for the Wicked profile](../no-rest-for-the-wicked/README.md#assemble-a-separate-wrapper), with the newer archives:

1. Extract the template. Move `Template-1.0.27.app` to `~/Games/STAR WARS Zero Company (Wine).app`.
2. Extract the engine into `Contents/SharedSupport/` and rename `wswine.bundle` to `wine`. `Contents/SharedSupport/wine/version` should read `wine sikarugir 11.0 (revision 1)`.
3. Set these `Contents/Info.plist` values with `plutil -replace`, then read them back:

| Key | Value |
|---|---|
| `D3DMETAL` | `1` |
| `WINEMSYNC` | `1` |
| `WINEDEBUG` | `-all` |
| `Program Name and Path` | `/Program Files (x86)/Steam/Steam.exe` |
| `CFBundleName` | `STAR WARS Zero Company (Wine)` |
| `CFBundleIdentifier` | a unique value, e.g. `com.SikarugirNavyWrapper.SWZeroCompany` |

4. Create the prefix and install Steam:

```sh
wrapper="$HOME/Games/STAR WARS Zero Company (Wine).app"
"$wrapper/Contents/MacOS/Sikarugir" WSS-wineprefixcreate
"$wrapper/Contents/MacOS/Sikarugir" WSS-installer "$HOME/Downloads/SteamSetup.exe"
```

The prefix command finished on its own. The installer command keeps running while Steam is open. Keep Steam's default `C:\Program Files (x86)\Steam` folder. The player signs in and installs the game in this Windows Steam client.

## Two first-launch problems

**1. Steam stays on "Running install script".** Steam runs the Visual C++ 2022 and DirectX June 2010 redistributables before the first launch. The Visual C++ installers exited with code 0. `DXSETUP.exe /silent` finished its work within about a minute, but Steam recorded its exit only about four minutes later. Wait a few minutes; cancelling and pressing Play again is the next thing to try. Steam then records exit code 0 and sets `HKLM\Software\Wow6432Node\Valve\Steam\Apps\CommonRedist\DirectX\Jun2010` `dxsetup=1`. If it keeps hanging, set that value while the prefix is stopped.

**2. "Microsoft Visual C++ 2015-2022 Redistributable (x64)" is required.** The game's Unreal launcher showed this dialog, and Steam recorded exit code `9001`. The redistributable *was* installed: Microsoft's 14.51 DLLs were in `system32`, and the `VC\Runtimes\x64` registry key was set. Wine loads its own builtin `msvcp140`, `vcruntime140`, and related DLLs first. The builtin `vcruntime140.dll` has no file version, so the launcher's check fails. The fix is to prefer the native DLLs, as `winetricks vcrun2022` does. Add the eight `native,builtin` entries listed in `profile.json` under `[Software\\Wine\\DllOverrides]` in the prefix's `user.reg`.

Edit `user.reg` only while no process of this wrapper runs, and keep a backup. The running `wineserver` holds the registry in memory and overwrites the file. `python3 tools/mac_gaming.py doctor star-wars-zero-company` reports whether the overrides are present.

## Play

Start the wrapper. Windows Steam opens; press Play. The first start compiles shaders for a while. The game data and saves are in `drive_c/users/Sikarugir/AppData/Local/SWZeroCompany/Saved`. The shipping build writes no Unreal log there.

- In this Sikarugir wrapper, **Option** is the Windows Alt key. **Option + Return** switches between full screen and a window. Command + Return does nothing.
- The game window has a fixed size; macOS cannot resize it by dragging. Choose windowed mode and a smaller resolution in the game's display settings instead. Edit `GameUserSettings.ini` only while the game is closed, because the game rewrites it on exit.
- On the first start, the game picked borderless full screen at the display's native resolution with dynamic resolution on. Its target frame rate was 30, with a minimum resolution of 74 %.
- Steam often stays running after the game exits. After Steam Cloud finishes, use **Steam > Exit** inside the Windows client.

## Open checks

- Exit through the game menu, then run `doctor` for the exit code and the last Cloud upload.
- Controller, audio devices, and longer sessions are untested.
- Windows players report start crashes with D3D12 GPU crash dumps. The workaround they report is `bNaniteEnabled=False` in `GameUserSettings.ini`. This was not needed here.

## Agent notes

On this Mac, `wine` started directly from a Claude Code shell exited with code 1 and no output once it tried to reach the running wineserver, with and without the sandbox and with `WINEMSYNC`, `WINEESYNC`, and the library paths set. `wine --version` worked, and the wrapper's own `Sikarugir` launcher worked when the player ran it. Prefer offline `user.reg` edits and the wrapper launcher over direct `wine` calls from an agent shell.
