#!/usr/bin/env bash

scriptDir=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")
source "${scriptDir}/../../set_pythonpath.sh"
tmux new -s "ATOP" "bash $scriptDir/run_atop_stream.sh"



