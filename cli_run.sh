#!/bin/bash

cd /usr/local/share/discord-linux-autoupdate/
./venv/bin/python3 main.py cli
./run_discord.sh "$@"