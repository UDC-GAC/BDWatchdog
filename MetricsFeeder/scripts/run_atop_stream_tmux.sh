#!/usr/bin/env bash

export scriptDir=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")
tmux new -s "ATOP" -d "bash $scriptDir/run_atop_stream.sh"
