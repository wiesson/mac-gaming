# Agent workflow

This public repository describes game profiles. Treat each machine as different from the tested reference. The user's request controls which profile to set up.

1. Read `README.md`, the selected `profiles/<slug>/profile.json`, and its `README.md`. Run `python3 tools/mac_gaming.py validate` and `doctor <slug>` before changing the machine.
2. Identify the Mac chip, macOS version, available storage, installed wrappers, running game/Steam processes, and the user's existing game library. Use official publisher sources for downloads; verify pinned hashes where provided. Never download installers from a lookalike Sikarugir site.
3. Keep a working prefix and installed game intact. Use a separate wrapper/prefix for experiments. If adopting an existing Steam game, clone or copy its game directory and manifests into the new prefix; never point two live Steam clients at one writable library.
4. Stop a running game only after the player has exited and Steam Cloud has finished syncing. Back up any registry or Steam config before edits. Use `tools/configure_nrftw.py` only for its matching profile and only while that Wine prefix is stopped.
5. Let the player enter account credentials and decide on EULAs. Do not read, copy, commit, or upload authentication data. Do not include complete logs, dumps, prefixes, saves, or private paths in this repository.
6. Verify the complete path: launcher starts, account is signed in, the game reaches gameplay, input and audio work, the game exits with code 0, and any cloud sync completes. Record what was observed and what remains untested. Do not infer FPS from a subjective report.
7. Keep changes to one profile at a time. If a working game needs tuning, compare one graphics setting in a repeatable scene before changing runtimes or renderers.

For the No Rest for the Wicked profile, the user may already have a CrossOver installation. CrossOver is the source of the successful DX11 settings, not a dependency of the free Sikarugir wrapper. The separate wrapper must work on its own before CrossOver is removed.
