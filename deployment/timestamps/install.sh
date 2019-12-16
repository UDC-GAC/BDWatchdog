#!/usr/bin/env bash
if [ -z ${BDWATCHDOG_DIR} ]
then
    echo "\$BDWATCHDOG_DIR is not set, check and source the config.sh file and try again"
    exit 0
fi

cd ${BDWATCHDOG_DIR}/TimestampsSnitch/
pip3 install -r requirements.txt
bash scripts/install/ubuntu/install-mongodb-dependencies.sh
cd ${BDWATCHDOG_DIR}/deployment/timestamps
