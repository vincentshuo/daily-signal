# Daily Signal

A quiet, daily reading feed for ideas found on YouTube.

## How it works

- HTML reading reports live under `Channel/<channel-name>/` and are published as-is.
- `build_index.py` regenerates the reading index from every HTML file in the project.
- `watch_sync.py` runs as a macOS LaunchAgent, waits for a 60-second quiet window, then rebuilds, commits, and pushes through the SSH remote.
- `.github/workflows/pages.yml` deploys the repository to GitHub Pages after every push to `main`.

The local sync path intentionally uses SSH and does not call GitHub CLI or depend on Automic Vault. GitHub Pages uses the Actions runtime token supplied by GitHub itself.

## Watcher controls

```sh
./install_watcher.sh
launchctl print "gui/$(id -u)/com.vincentshuo.daily-signal"
launchctl bootout "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.vincentshuo.daily-signal.plist"
```
