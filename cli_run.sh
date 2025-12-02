#!/bin/bash

cd /usr/local/share/discord-updater/
./venv/bin/python3 main.py cli
./run_discord.sh "$@"