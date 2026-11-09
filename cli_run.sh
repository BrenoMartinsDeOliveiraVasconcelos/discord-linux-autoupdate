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

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ ! -f "$script_dir/main.py" ]]; then
    script_dir=/usr/local/share/discord-updater
fi
cd "$script_dir" || exit 1
./venv/bin/python3 main.py cli "$channel" || exit $?
./run_discord.sh "$@"