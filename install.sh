#!/bin/bash

# CHeck if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root"
   exit 1
fi

script_path="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
git_path="$script_path/dl"
mkdir -p "$git_path"
cd "$git_path"
install_dir="/usr/local/share/discord-updater"
config_dir="/opt/discord-updater"

if command -v apt-get &> /dev/null; then
    echo "Dependency installation for Debian-based distributions has started."
    apt-get update
    apt-get install -y python3-venv git wget python3-tk

    echo "Dependencies installed."
else
    echo "This software only supports Debian-based distributions due Discord linux package format."
    exit 1
fi

# Clone the repository
git clone https://github.com/BrenoMartinsDeOliveiraVasconcelos/discord-linux-autoupdate.git .   

echo "Creating necessary directories..."
mkdir -p $install_dir
mkdir -p $config_dir

echo "Copying files..."
files_to_copy=("cli_run.sh" "gui_run.sh" "run_discord.sh" "main.py" "helpers.py" "gui.py" "icon" "config.json" "README.md" "LICENSE.md" "DISCLAIMER.md" "uninstall.sh" "requirements.txt" "desktop")

for file in "${files_to_copy[@]}"; do
    cp -f -r "$file" "$install_dir/"
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
cp -f -r cli_run.sh /usr/local/bin/discord-updater
cp -f -r gui_run.sh /usr/local/bin/discord-updater-gui

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

        cp -f desktop/dau_${channel}.desktop -r $desktop_file_path
        chown root:root $desktop_file_path
        chmod 755 $desktop_file_path
    done
fi

read -p "Do you want to kidnap Discord's .desktop file to run the updater? (y/n): "  kidnap_discord
if [[ "$kidnap_discord" == "y" || "$kidnap_discord" == "Y" ]]; then
    touch "$install_dir/kidnap"
fi

echo "Installation finished successfully."

echo "Removing post install trash."

rm -rf "$install_dir/requirements.txt"
rm -rf "$install_dir/desktop"
cd "$script_path"
rm -rf "$git_path"

echo "Done."

echo "Select one of these to do after installation:"
echo "1 - Run Discord Updater GUI"
echo "2 - Run Discord Updater CLI"
echo "3 - Exit"
read -p "Enter your choice (1/2/3): " post_install_choice

selected_channel="stable"
channels=("stable" "ptb" "canary")
if [[post_install_choice != 3]]; then
    read -p "Channel (stable/ptb/canary) [default: stable]: " selected_channel

    is_present=0
    for channel in "${channels[@]}"; do
        if [[ "$selected_channel" == "$channel" ]]; then
            is_present=1
            break
        fi
    done

    if [[ is_present == 0 ]]; then
        selected_channel="stable"
    fi
fi

if [[ "$post_install_choice" == "1" ]]; then
    discord-updater-gui -rd "$selected_channel"
elif [[ "$post_install_choice" == "2" ]]; then
    discord-updater -rd "$selected_channel"
else
    echo "Exiting."
fi