
# discord-linux-autoupdate

A small helper for Debian-based Linux distributions that automatically checks for and installs the latest Discord `.deb` package when one is available.

---

## **Features**

- **Auto-update**: Fetches the latest Discord `.deb` for the selected channel and installs it.
- **CLI & GUI**: Run headless via CLI or interactively with a basic GUI.
- **Safe downloads**: Verifies download and write integrity with MD5 checksum.

---

## **Requirements**

- **Debian/Ubuntu-based Linux** (due Discord's lack of packaging outside of .deb)
- **Python 3.8+**, `python3-venv` and `pip`.
- Python packages listed in `requirements.txt` (installer sets these up automatically).
- Optional GUI: `python3-tk`.

---

## **Installation (recommended)**

The repository includes `install.sh` which performs a one-time installation into `/usr/local/share/discord-updater` and creates launchers in `/usr/local/bin`. Optionally, it creates menu entries which also opens discord automatically after finishing execution.

Run the installer from the project folder:

```bash
sudo bash ./install.sh
```

---

## **Usage**

You can run the project either installed system-wide (recommended) or directly from the repository.

**Installed — system commands**

- CLI mode:

```bash
discord-updater        # runs the CLI updater
```

- GUI mode:

```bash
discord-updater-gui    # runs the GUI updater
```

Both launcher scripts support a channel argument (`stable`, `ptb`, `canary`) and the run-discord flag `--run-discord` (short `-rd`) to start Discord after updating.

**Direct**

From the project root you can run the Python entrypoint directly using the bundled virtualenv or system Python.

```bash
python3 main.py cli                  # CLI flow
python3 main.py gui                  # GUI flow (shows prompts)
python3 main.py gui-no-interrupt     # GUI but suppress informational dialogs
```

You may also pass a channel name, e.g. `python3 main.py cli canary`.

Note: Create 3 empty json files that cointains `{}` only on the same folder, which names are: `stable_last_saved.json`, `ptb_last_saved.json` and `canary_last_saved.json`

---

## **Configuration**

The repository includes a default `config.json`. When installed, a copy is used at `/opt/discord-updater/config.json` (the installer creates this file). Key config values:

- `url`: Template URL used to fetch Discord packages. `$` is replaced with the channel name.
- `download_path`: Directory where downloads are saved (default `/var/tmp/dau`).
- `retry_attempts`: Number of attempts to retry downloads/writes.
- `retry_delay`: Delay (seconds) between retry attempts.

Edit the installed config at `/opt/discord-updater/config.json` to change behavior after installing. When running directly from the repo the local `config.json` will be used as a fallback.

---

## **Examples & Flags**

- Run CLI and start Discord after update (stable channel):

```bash
discord-updater -rd
```

- Run GUI for the `canary` channel without informational popups:

```bash
discord-updater-gui canary -ni
```

Notes: `-rd` maps to `--run-discord`. The GUI wrapper supports `-ni` (`--no-interrupt`) to suppress info dialogs.

---

## **Uninstall**

You can run the uninstaller on the repo to delete all files.

```bash
sudo ./uninstall.sh
```

---
