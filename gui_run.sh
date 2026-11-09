#!/bin/bash

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ ! -f "$script_dir/main.py" ]]; then
    script_dir=/usr/local/share/discord-updater
fi
cd "$script_dir" || exit 1

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

./venv/bin/python3 main.py "$mode" "$channel" || exit $?
./run_discord.sh "$@"
