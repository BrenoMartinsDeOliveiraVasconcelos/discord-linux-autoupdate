from __future__ import annotations

import requests
import json
import os
import hashlib
import subprocess
import shutil
import time

CHANNELS = ['stable', 'ptb', 'canary']

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG_PATH = os.path.join(SCRIPT_DIR, 'config.json')
CONFIG_DIR = "/opt/discord-updater"
CONFIG_PATH = f"{CONFIG_DIR}/config.json"
DESKTOP_DIR = "/usr/share/applications"
DESKTOP_DOT_ARGS = ['-rd', '-ni']
EXEC_PATH = "/usr/local/bin/discord-updater-gui"

# Reading configuration must not require permission to write system files.
with open(DEFAULT_CONFIG_PATH) as config_file:
    CONFIG = json.load(config_file)
if os.path.isfile(CONFIG_PATH):
    with open(CONFIG_PATH) as config_file:
        CONFIG.update(json.load(config_file))

URL = CONFIG.get('url', "https://discord.com/api/download/$?platform=linux&format=")
DOWNLOAD_PATH = os.path.expanduser(CONFIG['download_path'])
RETRY_ATTEMPTS = int(CONFIG.get('retry_attempts', 3))
RETRY_DELAY = float(CONFIG.get('retry_delay', 5))
if RETRY_ATTEMPTS < 1 or RETRY_DELAY < 0:
    raise ValueError('retry_attempts must be positive and retry_delay nonnegative')
STATE_DIR = os.path.join(os.environ.get('XDG_STATE_HOME', os.path.expanduser('~/.local/state')),
                         'discord-updater')


def _state_path(channel):
    return os.path.join(STATE_DIR, f'{channel}_last_saved.json')


def _read_state(channel):
    try:
        with open(_state_path(channel)) as state_file:
            state = json.load(state_file)
        return state if isinstance(state, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def mark_installed(file_path, channel):
    # A successful download alone does not mean the update was installed.
    with open(file_path, 'rb') as package:
        digest = hashlib.md5(package.read()).hexdigest()
    os.makedirs(STATE_DIR, exist_ok=True)
    path = _state_path(channel)
    with open(path + '.tmp', 'w') as state_file:
        json.dump({'filename': os.path.basename(file_path), 'md5': digest,
                   'package_type': 'deb'}, state_file)
    os.replace(path + '.tmp', path)


def fetch_file(pkg: str = 'deb', channel: str = 'stable') -> str | bool:
    if pkg != 'deb':
        raise NotImplementedError("Only deb packages are supported.")
    if channel not in CHANNELS:
        raise ValueError(f'Invalid channel: {channel}')
    url = URL.replace('$', channel) + pkg
    for attempt in range(RETRY_ATTEMPTS):
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            content = response.content
            digest = hashlib.md5(content).hexdigest()
            # Only a plain MD5 ETag can be used as an integrity checksum.
            expected = response.headers.get('etag', '').strip('"')
            if expected.lower() != digest:
                raise ValueError('Download MD5 does not match the server ETag')
            break
        except (requests.RequestException, ValueError):
            if attempt + 1 == RETRY_ATTEMPTS:
                raise
            time.sleep(RETRY_DELAY)

    state = _read_state(channel)
    if state.get('md5') == digest and state.get('package_type') == pkg:
        print('No updates available.')
        return False

    os.makedirs(DOWNLOAD_PATH, exist_ok=True)
    import tempfile
    descriptor, path = tempfile.mkstemp(prefix=f'discord-{channel}-', suffix='.deb',
                                         dir=DOWNLOAD_PATH)
    os.close(descriptor)
    try:
        for attempt in range(RETRY_ATTEMPTS):
            try:
                with open(path, 'wb') as package:
                    package.write(content)
                with open(path, 'rb') as package:
                    if hashlib.md5(package.read()).hexdigest() != digest:
                        raise OSError('File write integrity verification failed')
                return path
            except OSError:
                if attempt + 1 == RETRY_ATTEMPTS:
                    raise
                time.sleep(RETRY_DELAY)
    except Exception:
        os.remove(path)
        raise


def get_elevate_cmd(elevate_command: str = 'auto') -> str:
    valid_elevate_cmds = ['auto', 'sudo', 'pkexec']
    if elevate_command not in valid_elevate_cmds:
        raise ValueError(f"Invalid elevate_cmd. Must be one of {valid_elevate_cmds}.")

    
    if elevate_command == 'auto':
        if shutil.which('pkexec') is not None:
            elevate_command = 'pkexec'
        else:
            elevate_command = 'sudo'

    return elevate_command


def install_file(file_path: str, elevate_command: str = 'auto') -> bool:
    if not file_path.endswith('.deb'):
        return False
    elevation = get_elevate_cmd(elevate_command)
    prefix = [] if os.geteuid() == 0 else [elevation]
    try:
        # apt installs the requested package and resolves its dependencies together.
        subprocess.check_call(prefix + ['apt-get', 'install', '-y', os.path.abspath(file_path)])
        return True
    except (subprocess.CalledProcessError, OSError):
        return False


def clear_downloads() -> None:
    if not os.path.isdir(DOWNLOAD_PATH):
        return
    retained = {_read_state(channel).get('filename') for channel in CHANNELS}
    for name in os.listdir(DOWNLOAD_PATH):
        if name in retained:
            continue
        if any(name.startswith(f'discord-{channel}-') for channel in CHANNELS) and name.endswith('.deb'):
            path = os.path.join(DOWNLOAD_PATH, name)
            if (os.path.isfile(path) and not os.path.islink(path)
                    and os.stat(path).st_uid == os.geteuid()):
                os.remove(path)


def replace_discord_desktop(elevate_command: str) -> bool:
    if not os.path.exists(os.path.join(SCRIPT_DIR, 'kidnap')):
        return False
    elevation = get_elevate_cmd(elevate_command)
    prefix = [] if os.geteuid() == 0 else [elevation]
    changed = False
    for channel in CHANNELS:
        name = 'discord.desktop' if channel == 'stable' else f'discord-{channel}.desktop'
        path = os.path.join(DESKTOP_DIR, name)
        if not os.path.isfile(path):
            continue
        with open(path) as desktop:
            lines = desktop.readlines()
        updated = [f'Exec={EXEC_PATH} {" ".join(DESKTOP_DOT_ARGS)} {channel} %U\n'
                   if line.startswith('Exec=') and EXEC_PATH not in line else line
                   for line in lines]
        if updated == lines:
            continue
        if not os.path.exists(path + '.original'):
            subprocess.check_call(prefix + ['cp', path, path + '.original'])
        process = subprocess.Popen(prefix + ['tee', path], stdin=subprocess.PIPE,
                                   stdout=subprocess.DEVNULL)
        process.communicate(input=''.join(updated).encode('utf-8'))
        if process.returncode:
            raise subprocess.CalledProcessError(process.returncode, process.args)
        changed = True
    return changed
