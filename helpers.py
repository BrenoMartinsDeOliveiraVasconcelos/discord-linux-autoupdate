import requests
import json
import os
import random
import hashlib
import datetime


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

def fetch_file(pkg: str = 'deb') -> str | bool:
    """
    Fetches a file from a remote server based on the package type.

    Args:
        pkg (str): The package type, either 'deb' or 'rpm'. Defaults to 'deb'.

    Returns:
        str: Path to the downloaded file.
        bool: False if no download was necessary.
    """

    if pkg != 'deb':
        raise NotImplementedError("Discord API only supports 'deb' packages on Linux at the moment.")

    url_req = URL + pkg
    response = requests.get(url_req)
    response.raise_for_status()

    content = b""
    headers = {}
    request_md5 = ""
    md5sum_content = ""

    # Check request integrity
    while True:
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

    file_name = ""
    while True:
        file_name = f"discord-{random.randint(0, 9999999)}.{pkg}"

        if not os.path.exists(os.path.join(DOWNLOAD_PATH, file_name)):
            break

    last_saved_json = json.load(open(LAST_SAVED_FILE, 'r'))
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

        with open(LAST_SAVED_FILE, 'w') as f:
            json.dump(last_saved_json, f, indent=4)

        # Write file and check write integrity

        while True:
            download_path_file = os.path.join(DOWNLOAD_PATH, file_name)
            with open(os.path.join(download_path_file), 'wb') as f:
                f.write(content)

            md5sum_file = hashlib.md5(open(download_path_file, 'rb').read()).hexdigest()
            if md5sum_file == request_md5:
                print("File write integrity verified.")
                break
            print("File write integrity failed. Retrying...")
            

        return os.path.join(DOWNLOAD_PATH, file_name)
    
    print("No download necessary.")
    return False






if __name__ == '__main__':
    fetch_file()
