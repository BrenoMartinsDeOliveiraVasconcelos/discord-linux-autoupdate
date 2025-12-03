#!/bin/bash

# CHeck if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root"
   exit 1
fi

script_path="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_path"
install_dir="/usr/local/share/discord-updater"
config_dir="/opt/discord-updater"

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
mkdir -p $config_dir

echo "Copying files..."
files_to_copy=("cli_run.sh" "gui_run.sh" "run_discord.sh" "main.py" "helpers.py" "gui.py" "icon" "config.json" "README.md" "LICENSE.md" "DISCLAIMER.md" "uninstall.sh" "requirements.txt" "desktop")

for file in "${files_to_copy[@]}"; do
    cp -r "$file" "$install_dir/"
done

echo "Creating necessary files..."
channels=("stable" "ptb" "canary")
for channel in "${channels[@]}"; do
    if [ ! -f "$install_dir/${channel}_last_saved.json" ]; then
        touch "$install_dir/${channel}_last_saved.json"
        echo "{}" | tee "$install_dir/${channel}_last_saved.json" > /dev/null
    fi
done

if [ ! -f "$config_dir/config.json" ]; then
    touch "$config_dir/config.json"
    echo "{}" | tee "$config_dir/config.json" > /dev/null
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
chown -R root:root "$config_dir"

echo "Setting permissions..."
chmod 755 /usr/local/bin/discord-updater
chmod 755 /usr/local/bin/discord-updater-gui
chmod -R 755 "$install_dir"
chmod 755 "$install_dir/run_discord.sh"
chmod 666 "$install_dir/config.json"
for channel in "${channels[@]}"; do
    chmod 666 "$install_dir/${channel}_last_saved.json"
done
chmod -R 755 "$config_dir"
chmod 666 "$config_dir/config.json"


read -p "Installation is complete. Do you want to create a Desktop menu shortcut (GUI)? (y/n): " create_shortcut
if [[ "$create_shortcut" == "y" || "$create_shortcut" == "Y" ]]; then
    wanted_channels=()
    for channel in "${channels[@]}"; do
        read -p "Create an entry for $channel channel? (y/n): " include_channel
        if [[ "$include_channel" == "y" || "$include_channel" == "Y" ]]; then
            wanted_channels+=("$channel")
        fi
    done

    for channel in "${wanted_channels[@]}"; do
        desktop_file_path="/usr/share/applications/dau_${channel}.desktop"
        echo "Creating .desktop file at $desktop_file_path"

        cp desktop/dau_${channel}.desktop -r $desktop_file_path
        chown root:root $desktop_file_path
        chmod 755 $desktop_file_path
    done
fi

echo "Installation finished successfully."

echo "Removing post install trash."

rm -rf "$install_dir/requirements.txt"
rm -rf "$install_dir/desktop"

echo "Done."