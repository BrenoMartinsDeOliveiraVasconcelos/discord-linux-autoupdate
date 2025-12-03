#!/bin/bash

cd /usr/local/share/discord-updater/

mode="gui"

channel_args=("stable" "ptb" "canary")
channel="stable"

for arg in "$@"; do
    for ch in "${channel_args[@]}"; do
        if [[ "$arg" == "$ch" ]]; then
            channel="$ch"
        fi
    done
done

for i in "$@"; do
    if [[ $i == "--no-interrupt" || $i == "-ni" ]]; then
        mode="gui-no-interrupt"
    fi
done

./venv/bin/python3 main.py $mode $channel
./run_discord.sh "$@"
