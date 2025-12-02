#!/bin/bash

# CHeck if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root"
   exit 1
fi

script_path="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_path"
install_dir="/usr/local/share/discord-linux-autoupdate"

if command -v apt-get &> /dev/null; then
    echo "Dependency installation for Debian-based distributions has started."
    apt-get update
    userwantsgui='n'
    read -p "[OPTIONAL] Do you want to install the GUI dependencies? (y/n): " userwantsgui

    if [[ "$userwantsgui" == "y" || "$userwantsgui" == "Y" ]]; then
        apt-get install -y python3-tk
    fi

    apt-get install -y python3-venv
else
    echo "This software only supports Debian-based distributions due Discord linux package format."
    exit 1
fi


echo "Creating necessary directories..."
mkdir -p $install_dir

echo "Copying files..."
cp -r ./* $install_dir

echo "Creating necessary files..."
touch "$install_dir/last_saved.json"
echo "{}" | tee "$install_dir/last_saved.json" > /dev/null

echo "Creating launchers..."
cp -r cli_run.sh /usr/local/bin/discord-updater
cp -r gui_run.sh /usr/local/bin/discord-updater-gui

echo "Installing virtual environment and dependencies..."
cd $install_dir
python3 -m venv venv

source ./venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

echo "Chowning files to root"
chown -R root:root "$install_dir"
chown root:root "/usr/local/bin/discord-updater"
chown root:root "/usr/local/bin/discord-updater-gui"

echo "Setting permissions..."
chmod a+x /usr/local/bin/discord-updater
chmod a+x /usr/local/bin/discord-updater-gui
chmod -R a+rX "$install_dir"
chmod a+rX "$install_dir/run_discord.sh"
chmod a+rw "$install_dir/config.json"
chmod a+rw "$install_dir/last_saved.json"
