import requests
import json
import os
import random
import hashlib
import datetime
import subprocess
import shutil
import time
import traceback

CHANNELS = ['stable', 'ptb', 'canary']

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
print(SCRIPT_DIR)
DEFAULT_CONFIG_PATH = os.path.join(SCRIPT_DIR, 'config.json')
CONFIG_DIR = "/opt/discord-updater"
CONFIG_PATH = f"{CONFIG_DIR}/config.json"
DESKTOP_DIR = "/usr/share/applications"
DESKTOP_DOT_ARGS = ['-rd', "-ni"]
EXEC_PATH = "/usr/local/bin/discord-updater-gui"

# Load user config if it exists, otherwise create it with default values
CONFIG = json.load(open(CONFIG_PATH, 'r'))
if CONFIG != {}:
    with open(CONFIG_PATH, 'r') as f:
        CONFIG = json.load(f)
else:
    with open(DEFAULT_CONFIG_PATH, 'r') as f:
        CONFIG = json.load(f)
    with open(CONFIG_PATH, 'w+') as f:
        json.dump(CONFIG, f, indent=4)

# Add missing keys from default config
with open(DEFAULT_CONFIG_PATH, 'r') as f:
    default_config = json.load(f)

for key, value in default_config.items():
    if key not in CONFIG:
        CONFIG[key] = value

json.dump(CONFIG, open(CONFIG_PATH, 'w+'), indent=4)

# Config variables
URL = "https://discord.com/api/download/$?platform=linux&format="
DOWNLOAD_PATH = CONFIG['download_path']
RETRY_ATTEMPTS = CONFIG.get('retry_attempts', 3)
RETRY_DELAY = CONFIG.get('retry_delay', 5)

# Ensure download path exists
if not os.path.exists(DOWNLOAD_PATH):
    os.makedirs(DOWNLOAD_PATH, exist_ok=True)

def fetch_file(pkg: str = 'deb', channel: str = 'stable') -> str | bool:
    """
    Fetches a file from a remote server based on the package type.

    Args:
        pkg (str): The package type, either 'deb' or 'rpm'. Defaults to 'deb'.
        channel (str): The release channel, either 'stable', 'ptb', or 'canary'. Defaults to 'stable'.

    Returns:
        str: Path to the downloaded file.
        bool: False if no download was necessary.
    """

    if pkg != 'deb':
        raise NotImplementedError("Discord API only supports 'deb' packages on Linux at the moment.")

    url_req = URL.replace("$", channel) + pkg
    last_saved_file = os.path.join(SCRIPT_DIR, f'{channel}_last_saved.json')

    content = b""
    headers = {}
    request_md5 = ""
    md5sum_content = ""
    # Check request integrity
    tries = 0
    while tries < RETRY_ATTEMPTS:
        tries += 1
        print("Fetching file...", flush=True)
        response = requests.get(url_req)
        response.raise_for_status()
        content = response.content
        headers = response.headers
        request_md5 = headers["etag"].replace('"', '')

        md5sum_content = hashlib.md5(content).hexdigest()
        if request_md5 == md5sum_content:
            print("Request integrity verified.")
            break

        print("Request integrity failed. Retrying...")
        time.sleep(RETRY_DELAY)
    else:
        raise Exception("Failed to verify request integrity after multiple attempts.")
    
    tries = 0

    file_name = ""
    while True:
        file_name = f"discord-{channel}-{random.randint(0, 9999999)}.{pkg}"

        if not os.path.exists(os.path.join(DOWNLOAD_PATH, file_name)):
            break

    last_saved_json = json.load(open(last_saved_file, 'r'))
    should_download = False

    if last_saved_json == {}:
        should_download = True
    
    if not should_download:
        if last_saved_json['md5'] != request_md5:
            should_download = True

        if pkg != last_saved_json['package_type']:
            should_download = True

        if not os.path.exists(os.path.join(DOWNLOAD_PATH, last_saved_json['filename'])):
            should_download = True


    if should_download:
        last_saved_json['filename'] = file_name
        last_saved_json['md5'] = headers["etag"].replace('"', '')
        last_saved_json["modified_time"] = headers["last-modified"]
        last_saved_json["download_time"] = str(datetime.datetime.now())
        last_saved_json["package_type"] = pkg

        with open(last_saved_file, 'w') as f:
            json.dump(last_saved_json, f, indent=4)

        # Write file and check write integrity

        while tries < RETRY_ATTEMPTS:
            tries += 1
            download_path_file = os.path.join(DOWNLOAD_PATH, file_name)
            with open(os.path.join(download_path_file), 'wb') as f:
                f.write(content)

            md5sum_file = hashlib.md5(open(download_path_file, 'rb').read()).hexdigest()
            if md5sum_file == request_md5:
                print("File write integrity verified.")
                break
            print("File write integrity failed. Retrying...")
            time.sleep(RETRY_DELAY)
            

        return os.path.join(DOWNLOAD_PATH, file_name)
    
    print("No download necessary.")
    return False


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


def install_file(file_path: str, elevate_command: str = 'auto') -> None:
    """
    Installs the downloaded file using the appropriate package manager.

    Args:
        file_path (str): Path to the downloaded file.
        elevate_command (str): Command to use for privilege elevation. Options are 'auto', 'sudo', or 'pkexec'. Defaults to 'auto'.

    Returns:
        bool: True if installation was successful, False otherwise.

    """
    pkg_type = file_path.split('.')[-1]
    elevate_command = get_elevate_cmd(elevate_command)

    if pkg_type == 'deb':
        apt_fix = False
        try:
            subprocess.check_call([f'{elevate_command}', 'dpkg', '-i', file_path])
            print(f"Successfully installed {file_path} using dpkg.")
            return True   
        except subprocess.CalledProcessError:
            apt_fix = True
        except FileNotFoundError:
            print("Error: Could not find 'sudo', 'pkexec' or 'dpkg'. Are you on a Debian-based system?")
            return False
        
        if apt_fix:
            try:
                subprocess.check_call([f'{elevate_command}', 'apt-get', '-f', 'install'])
                print(f"Successfully fixed dependencies for {file_path} using apt-get.")
                return True
            except subprocess.CalledProcessError:
                print(f"Failed to fix dependencies for {file_path} using apt-get.")
                return False
    else:
        return False


def clear_downloads() -> None:
    """
    Clears all downloaded files in the download directory.
    """

    for file in os.listdir(DOWNLOAD_PATH):
        file_path = os.path.join(DOWNLOAD_PATH, file)
        for channel in CHANNELS:
            last_saved_file = os.path.join(SCRIPT_DIR, f'{channel}_last_saved.json')
            last_saved_json = json.load(open(last_saved_file, 'r'))
            try:
                if os.path.isfile(file_path) and file != last_saved_json["filename"] and channel in file:
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
            except KeyError:
                continue
            except Exception as e:
                print(f"Error deleting file {file_path}:\n {traceback.format_exc()}")


def replace_discord_desktop(elevate_command: str) -> bool:
    """
    Replaces the Discord desktop entry with the one from the updater.
    """
    if "kidnap" in os.listdir(SCRIPT_DIR):
        for channel in CHANNELS:
            discord_desktop = f"discord-{channel}.desktop"

            if channel == "stable":
                discord_desktop = "discord.desktop"

            elevate_command = get_elevate_cmd(elevate_command)
            desktop_file_path = os.path.join(DESKTOP_DIR, discord_desktop)
            if os.path.exists(desktop_file_path):
                print(f"Updating {desktop_file_path}")
                content = open(desktop_file_path, 'r').readlines()
                for line in content:
                    if line.startswith("Exec=") and EXEC_PATH not in line:
                        exec_path_w_args = EXEC_PATH + " " + " ".join(DESKTOP_DOT_ARGS) + " " + channel
                        new_line = f"Exec={exec_path_w_args}\n"
                        print(new_line)
                        content[content.index(line)] = new_line

                        # Create a copy of the original file
                        subprocess.check_call([elevate_command, 'cp', desktop_file_path, desktop_file_path + '.original'])  

                        new_content = "".join(content)
                        try:
                            p = subprocess.Popen(
                                [elevate_command, 'tee', desktop_file_path], 
                                stdin=subprocess.PIPE, 
                                stdout=subprocess.DEVNULL
                            )
                            p.communicate(input=new_content.encode('utf-8'))
                            
                            if p.returncode == 0:
                                return True
                            else:
                                raise subprocess.CalledProcessError(p.returncode, p.args)
                        except Exception as e:
                            raise e
                    else:
                        raise FileNotFoundError(f"Could not find {desktop_file_path}")
