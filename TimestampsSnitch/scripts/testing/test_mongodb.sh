#!/usr/bin/env bash

scriptDir=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")
source "${scriptDir}/../../../set_pythonpath.sh"

TIMESTAMPING_PATH=${BDWATCHDOG_PATH}/TimestampsSnitch/src/timestamping/
MONGODB_PATH=${BDWATCHDOG_PATH}/TimestampsSnitch/src/mongodb/

python3 "${TIMESTAMPING_PATH}/signal_experiment.py" start experiment0 --push
python3 "${TIMESTAMPING_PATH}/signal_test.py" start experiment0 test0 --push
python3 "${TIMESTAMPING_PATH}/signal_test.py" end experiment0 test0 --push
python3 "${TIMESTAMPING_PATH}/signal_test.py" start experiment0 test1 --push
python3 "${TIMESTAMPING_PATH}/signal_test.py" end experiment0 test1 --push
python3 "${TIMESTAMPING_PATH}/signal_test.py" start experiment0 test2 --push
python3 "${TIMESTAMPING_PATH}/signal_test.py" end experiment0 test2 --push
python3 "${TIMESTAMPING_PATH}/signal_experiment.py" end experiment0 --push

rm -f docs.txt
python3 "${TIMESTAMPING_PATH}/signal_experiment.py" start experiment1 >> docs.txt
python3 "${TIMESTAMPING_PATH}/signal_test.py" start experiment1 test0 >> docs.txt
python3 "${TIMESTAMPING_PATH}/signal_test.py" end experiment1 test0 >> docs.txt
python3 "${TIMESTAMPING_PATH}/signal_test.py" start experiment1 test1 >> docs.txt
python3 "${TIMESTAMPING_PATH}/signal_test.py" end experiment1 test1 >> docs.txt
python3 "${TIMESTAMPING_PATH}/signal_test.py" start experiment1 test2 >> docs.txt
python3 "${TIMESTAMPING_PATH}/signal_test.py" end experiment1 test2 >> docs.txt
python3 "${TIMESTAMPING_PATH}/signal_experiment.py" end experiment1 >> docs.txt
cat docs.txt | python3 ${MONGODB_PATH}/mongodb_agent.py
rm docs.txt

python3 "${TIMESTAMPING_PATH}/signal_experiment.py" info ALL

python3 "${TIMESTAMPING_PATH}/signal_experiment.py" info experiment0
python3 "${TIMESTAMPING_PATH}/signal_test.py" info experiment0 ALL
python3 "${TIMESTAMPING_PATH}/signal_test.py" delete experiment0 test0
python3 "${TIMESTAMPING_PATH}/signal_test.py" delete experiment0 test1
python3 "${TIMESTAMPING_PATH}/signal_test.py" delete experiment0 test2
python3 "${TIMESTAMPING_PATH}/signal_experiment.py" delete experiment0
python3 "${TIMESTAMPING_PATH}/signal_experiment.py" info experiment0

python3 "${TIMESTAMPING_PATH}/signal_experiment.py" info experiment1
python3 "${TIMESTAMPING_PATH}/signal_test.py" info experiment1 ALL
python3 "${TIMESTAMPING_PATH}/signal_test.py" delete experiment1 test0
python3 "${TIMESTAMPING_PATH}/signal_test.py" delete experiment1 test1
python3 "${TIMESTAMPING_PATH}/signal_test.py" delete experiment1 test2
python3 "${TIMESTAMPING_PATH}/signal_experiment.py" delete experiment1
python3 "${TIMESTAMPING_PATH}/signal_experiment.py" info experiment1

python3 "${TIMESTAMPING_PATH}/signal_experiment.py" info ALL






