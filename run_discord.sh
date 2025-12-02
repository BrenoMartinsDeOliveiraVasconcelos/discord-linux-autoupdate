#!/bin/bash

if [[ $# -ge 1 ]]; then
    if [[ $1 == "--run-discord" || $1 == "-rd" ]]; then
        discord &>/dev/null &
    fi
fi