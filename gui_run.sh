#!/bin/bash

cd /usr/local/share/discord-updater/

arg="gui"

for i in "$@"; do
    if [[ $i == "--no-interrupt" || $i == "-ni" ]]; then
        arg="gui-no-interrupt"
    fi
done

./venv/bin/python3 main.py $arg
./run_discord.sh "$@"
