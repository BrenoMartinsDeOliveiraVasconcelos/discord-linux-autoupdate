# discord-linux-autoupdate

A small helper for Debian-based Linux distributions that automatically checks for and installs the latest Discord .deb package when one is available. It supports both command-line and GUI. Currently, it only supports Debian/Ubuntu based systems due Discord only offically packaging on .deb and .tar.gz.
---

## Features

- Automatically fetches the latest Discord Linux (.deb) package
- Install updates automatically (CLI or GUI flows)
- Thin, portable Python project that runs inside a virtualenv
- Optional GUI (requires python3-tk)

---

## Requirements

- Debian-based Linux distribution (the project uses apt-based install scripts)
- Python 3.8+ (system python) and python3-venv
- pip and the `requests` package (listed in `requirements.txt`)
- Optional for GUI: `python3-tk`

The project currently targets Debian-style distributions because it expects Discord in .deb format.

---

## Installation (recommended)

The repository includes `install.sh` which performs a one-time installation into `/usr/local/share/discord-linux-autoupdate` and creates launchers in `/usr/local/bin`.

Run the installer from the project folder:

```bash
sudo bash ./install.sh
```

What `install.sh` does:

- Installs optional GUI dependencies if desired.
- Creates /usr/local/share/discord-linux-autoupdate and copies project files there
- Creates a virtual environment and installs `requirements.txt`
- Adds two launchers to `/usr/local/bin`: `discord-updater` (CLI) and `discord-updater-gui` (GUI), copying the wrapper scripts
- Ensures file permissions and minimal configuration are set

After the script finishes you can run the CLI or GUI commands explained below.

---

## Usage

You can use the project in two ways: installed system-wide (via install script) or run directly from the repository.

### Installed - system commands

- CLI mode (checks & auto-installs):

```bash
discord-updater        # runs the CLI updater
```

- GUI mode (checks, auto-installs & shows prompts graphically):

```bash
discord-updater-gui    # runs the GUI updater
```

Both scripts will also attempt to optionally start Discord after updating if passed the `--run-discord` (shortly, `-rd`) argument.

### Directly

If you do not want to run the installer, or you are developing locally, run the Python entrypoint directly from the project directory.

Run the CLI flow:

```bash
python3 main.py cli
```

Run the GUI flow (interactive):

```bash
python3 main.py gui
```

Run the GUI flow but suppress informational dialogs (only show errors):

```bash
python3 main.py gui-no-interrupt
```

To auto-start the actual Discord binary after update, pass the `--run-discord` or `-rd` argument to the wrapper scripts (see `cli_run.sh` and `gui_run.sh`).

---

## Uninstall

Remove the installed directory and launchers:

```bash
sudo rm -rf /usr/local/share/discord-linux-autoupdate
sudo rm -f /usr/local/bin/discord-updater /usr/local/bin/discord-updater-gui
```

---

## Contributing

Contributions are welcome. Please open issues for bugs or feature requests and PRs for fixes/improvements.

---
