#!/usr/bin/env bash

scriptDir=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")

tmux new -d -s "EVE_TIMES" "bash $scriptDir/start_eve_server.sh"
