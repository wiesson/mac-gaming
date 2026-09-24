# Mac gaming on Apple Silicon

Tested game profiles and instructions for an AI coding agent to set up Windows games on a Mac. The agent inspects the actual machine, follows one profile, performs the reversible setup, and checks the result with the player. **You supply your own game license and sign in yourself.** This repository contains no game, Wine, Apple toolkit, or account binaries.

## Profiles

| Game | Store | Tested route | Guide |
|---|---|---|---|
| No Rest for the Wicked | Steam | Free Sikarugir wrapper, Wine 10, D3DMetal, Windows Steam | [Profile](profiles/no-rest-for-the-wicked/README.md) |
| Diablo IV | Battle.net | Custom Wine 11 based runtime, D3DMetal for the game and DXMT for Battle.net | [Profile](profiles/diablo-iv/README.md) |

Both are observations from one M3 Max running macOS 27.0. They are starting points, not compatibility promises or FPS benchmarks.

## Agent-first setup

Clone this repository into your Games folder:

```sh
git clone https://github.com/wiesson/mac-gaming.git "$HOME/Games/mac-gaming"
cd "$HOME/Games/mac-gaming"
python3 tools/mac_gaming.py list
python3 tools/mac_gaming.py doctor no-rest-for-the-wicked
```

Then ask your coding agent:

> Read `AGENTS.md` and `profiles/no-rest-for-the-wicked/README.md`. Set up my Steam copy of No Rest for the Wicked on this Mac. Inspect existing installations first, keep working prefixes and saves intact, and verify the game with me.

For Diablo IV, replace the profile path with `profiles/diablo-iv/README.md`. `doctor` reads local files only. It does not install software or send diagnostics anywhere. An agent can use the profile's exact source links and checks to perform the setup; account login and license agreement decisions stay with you.

## How profiles work

Each game has a `profiles/<slug>/profile.json` for machine-readable identity and a `README.md` with the verified setup, source versions, steps, checks, and limits. The [agent instructions](AGENTS.md) define the shared workflow. Run `python3 tools/mac_gaming.py validate` after editing profiles.

The [existing Diablo IV notes](docs/setup.md) and [technical investigation](docs/technical-notes.md) remain available. Its runtime is a matched custom bundle, so its profile deliberately does not claim a one-command clean install.

Documentation and included tools: [MIT license](LICENSE). Wine, Sikarugir, Apple's D3DMetal, Steam, Battle.net, and games have their own licenses.
