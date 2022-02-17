#!/usr/bin/env bash

scriptDir=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")
source "${scriptDir}/../../../set_pythonpath.sh"

TIMESTAMPING_PATH=${BDWATCHDOG_PATH}/TimestampsSnitch/src/timestamping/
MONGODB_PATH=${BDWATCHDOG_PATH}/TimestampsSnitch/src/mongodb/

python3 "${TIMESTAMPING_PATH}/signal_experiment.py" start TEST0 | python3 "${MONGODB_PATH}/mongodb_agent.py"
python3 "${TIMESTAMPING_PATH}/signal_test.py" start TEST0 APP0  | python3 "${MONGODB_PATH}/mongodb_agent.py"
python3 "${TIMESTAMPING_PATH}/signal_test.py" end TEST0 APP0  | python3 "${MONGODB_PATH}/mongodb_agent.py"
python3 "${TIMESTAMPING_PATH}/signal_experiment.py" end TEST0 | python3 "${MONGODB_PATH}/mongodb_agent.py"
