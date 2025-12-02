#!/bin/bash

cd /usr/local/share/discord-linux-autoupdate/

arg="gui"

for i in "$@"; do
    if [[ $i == "--no-interrupt" || $i == "-ni" ]]; then
        arg="gui-no-interrupt"
    fi
done

./venv/bin/python3 main.py $arg
./run_discord.sh "$@"
