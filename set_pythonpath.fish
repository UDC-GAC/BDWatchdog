#!/usr/bin/env fish

set -l scriptDir (realpath (dirname (status -f)))
export PYTHONPATH=$scriptDir

export BDWATCHDOG_PATH=$scriptDir
export SERVERLESS_PATH=$scriptDir/../ServerlessContainers/
export PYTHONPATH=$BDWATCHDOG_PATH:$SERVERLESS_PATH
