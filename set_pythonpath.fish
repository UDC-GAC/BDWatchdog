#!/usr/bin/env fish

set -l scriptDir (realpath (dirname (status -f)))

export BDWATCHDOG_PATH=$scriptDir/
if test -z "$SERVERLESS_PATH"
    set -gx SERVERLESS_PATH $scriptDir/../ServerlessContainers/
end
export PYTHONPATH=$BDWATCHDOG_PATH:$SERVERLESS_PATH
