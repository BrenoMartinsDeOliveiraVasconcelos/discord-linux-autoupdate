#!/bin/bash

channel_args=("stable" "ptb" "canary")
channel="stable"

for arg in "$@"; do
    for ch in "${channel_args[@]}"; do
        if [[ "$arg" == "$ch" ]]; then
            channel="$ch"
        fi
    done
done

cd /usr/local/share/discord-updater/
./venv/bin/python3 main.py cli $channel
./run_discord.sh "$@"