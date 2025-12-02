import requests
import json
import os
import random
import hashlib
import base64


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, 'config.json')
CONFIG = json.load(open(CONFIG_PATH, 'r'))

# Config variables
URL = CONFIG['url']
DOWNLOAD_PATH = CONFIG['download_path']
LAST_SAVED_FILE = os.path.join(SCRIPT_DIR, 'last_saved.json')

# Ensure download path exists
if not os.path.exists(DOWNLOAD_PATH):
    os.makedirs(DOWNLOAD_PATH, exist_ok=True)

# Ensure last saved file exists
if not os.path.exists(LAST_SAVED_FILE):
    with open(LAST_SAVED_FILE, 'w') as f:
        f.write('{}')

def fetch_file(pkg: str = 'deb'):
    """
    Fetches a file from a remote server based on the package type.

    Args:
        pkg (str): The package type, either 'deb' or 'rpm'. Defaults to 'deb'.

    Returns:
        str: Path to the downloaded file.
    """

    url_req = URL + pkg
    response = requests.get(url_req)
    response.raise_for_status()
    content = response.content
    headers = response.headers

    file_name = ""
    while True:
        file_name = f"discord-{random.randint(0, 9999999)}.{pkg}"

        if not os.path.exists(os.path.join(DOWNLOAD_PATH, file_name)):
            break

    last_saved_json = json.load(open(LAST_SAVED_FILE, 'r'))

    if last_saved_json == {}:
        last_saved_json['filename'] = file_name
        last_saved_json['md5'] = headers["etag"].replace('"', '')
        last_saved_json["modified_time"] = headers["last-modified"]

        with open(LAST_SAVED_FILE, 'w') as f:
            json.dump(last_saved_json, f, indent=4)

    # Write file
    with open(os.path.join(DOWNLOAD_PATH, file_name), 'wb') as f:
        f.write(content)

    return os.path.join(DOWNLOAD_PATH, file_name)


if __name__ == '__main__':
    fetch_file()
