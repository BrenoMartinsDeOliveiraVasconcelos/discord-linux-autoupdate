#!/bin/bash

# CHeck if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root"
   exit 1
fi

rm -rf /usr/local/share/discord-updater
rm -f /usr/local/bin/discord-updater /usr/local/bin/discord-updater-gui
rm -rf /opt/discord-updater
rm -rf /var/tmp/dau

# Look for menu entries
pattern="dau_*.desktop"
desktop_dirs=("/usr/share/applications")
for dir in "${desktop_dirs[@]}"; do
    if [ -d "$dir" ]; then
        for file in "$dir"/$pattern; do
            if [ -f "$file" ]; then
                rm -f "$file"
            fi
        done
    fi
done

echo "Discord Updater has been uninstalled."
