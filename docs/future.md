# Future ideas

Things worth a look later. Nothing here is set up yet.

## NotProton: Steam Play in macOS Steam

- Repo: https://github.com/NotProtonNot/NotProton (GPL-3, first release 2026-09-23, v1.1.5 on 2026-10-10)
- What it does: switches on the hidden Steam Play feature in macOS Steam. Windows games then get a normal Play button and run through a patched copy of CrossOver/Wine. It also ships macOS ports of Proton parts (`lsteamclient`, `steam-helper`) for achievements and the overlay.
- Install: `brew install --cask notprotonnot/notproton/notproton`
- Requirements: **a paid CrossOver** (26.3 or Preview 20261006; NotProton copies and patches it, with no free Wine option). It is pinned to Steam client builds 1788652215 or 1790121765.
- Recommended setup: Rosetta runtime as the default, FEX per game.
- Known issues (2026-10-11): the Play button disappears after a Steam restart (#92), Gatekeeper blocks it on macOS 27.2 (#52), no winecfg or DLL overrides (#65), and some games fail (Diablo IV #77).
- Our take: it is about convenience, not FPS. It uses the same D3DMetal layer as our Sikarugir setup. It's only worth trying if we buy CrossOver anyway.

## NRftW: loud fans

The fans are loud because the GPU runs at full load, and changing the Wine layer won't fix that. Try these first: cap the frame rate at 60 (or 45–50), turn on VSync, use FSR Quality, set shadows and volumetrics to High, and if needed use macOS Low Power Mode.
