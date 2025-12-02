#!/bin/bash

# CHeck if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root"
   exit 1
fi

script_path="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_path"
install_dir="/usr/local/share/discord-updater"

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
if [ ! -f "$install_dir/last_saved.json" ]; then
    touch "$install_dir/last_saved.json"
    echo "{}" | tee "$install_dir/last_saved.json" > /dev/null
fi

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
chmod 755 /usr/local/bin/discord-updater
chmod 755 /usr/local/bin/discord-updater-gui
chmod -R 755 "$install_dir"
chmod 755 "$install_dir/run_discord.sh"
chmod 666 "$install_dir/config.json"
chmod 666 "$install_dir/last_saved.json"


read -p "Installation is complete. Do you want to create a Desktop menu shortcut (GUI)? (y/n): " create_shortcut
if [[ "$create_shortcut" == "y" || "$create_shortcut" == "Y" ]]; then
    desktop_file_path="/usr/share/applications/dau.desktop"
    echo "Creating .desktop shortcut at $desktop_file_path"

    cp dau.desktop -r $desktop_file_path
    chown root:root $desktop_file_path
    chmod 755 $desktop_file_path
fi
