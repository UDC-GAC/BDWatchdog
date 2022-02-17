#!/usr/bin/env bash
scriptDir=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")

export BDWATCHDOG_PATH=$scriptDir/
export SERVERLESS_PATH=$scriptDir/../ServerlessContainers/
export PYTHONPATH=$BDWATCHDOG_PATH:$SERVERLESS_PATH


