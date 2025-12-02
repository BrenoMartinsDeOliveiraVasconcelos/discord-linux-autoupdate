#!/bin/bash

script_path="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_path"
install_dir="/usr/local/share/discord-linux-autoupdate"

if command -v apt-get &> /dev/null; then
    echo "Dependency installation for Debian-based distributions has started."
    sudo apt-get update
    userwantsgui='n'
    read -p "[OPTIONAL] Do you want to install the GUI dependencies? (y/n): " userwantsgui

    if [[ "$userwantsgui" == "y" || "$userwantsgui" == "Y" ]]; then
        sudo apt-get install -y python3-tk
    fi

    sudo apt-get install -y python3-venv
else
    echo "This software only supports Debian-based distributions due Discord linux package format."
    exit 1
fi


echo "Creating necessary directories..."
sudo mkdir -p $install_dir

echo "Copying files..."
sudo cp -r ./* $install_dir

echo "Creating necessary files..."
sudo touch "$install_dir/last_saved.json"
echo "{}" | sudo tee "$install_dir/last_saved.json" > /dev/null

echo "Creating launchers..."
sudo cp -r cli_run.sh /usr/local/bin/discord-updater
sudo cp -r gui_run.sh /usr/local/bin/discord-updater-gui

echo "Chowning files to root"
sudo chown -R root:root "$install_dir"
sudo chown root:root "/usr/local/bin/discord-updater"
sudo chown root:root "/usr/local/bin/discord-updater-gui"

echo "Setting permissions..."
sudo chmod a+x /usr/local/bin/discord-updater
sudo chmod a+x /usr/local/bin/discord-updater-gui
sudo chmod -R a+rX "$install_dir"
sudo chmod a+rw "$install_dir/config.json"
sudo chmod a+rw "$install_dir/last_saved.json"

echo "Installing virtual environment and dependencies..."
cd $install_dir
python3 -m venv venv

source ./venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
