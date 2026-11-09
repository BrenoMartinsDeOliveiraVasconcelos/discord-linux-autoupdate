#!/bin/bash
channel=stable
run=false
for arg in "$@"; do
    case "$arg" in
        stable|ptb|canary) channel="$arg" ;;
        --run-discord|-rd) run=true ;;
    esac
done
if "$run"; then
    case "$channel" in
        stable) command=discord ;;
        ptb) command=discord-ptb ;;
        canary) command=discord-canary ;;
    esac
    urls=()
    for arg in "$@"; do
        case "$arg" in
            discord://*|https://*) urls+=("$arg") ;;
        esac
    done
    "$command" "${urls[@]}" &>/dev/null &
fi
