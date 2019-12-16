#!/usr/bin/env bash
source ../config.sh
if [ -z ${BDWATCHDOG_DIR} ]
then
    echo "\$BDWATCHDOG_DIR is not set, check and source the config.sh file and try again"
    exit 0
fi
systemctl restart mongodb
cd ${BDWATCHDOG_DIR}/TimestampsSnitch/src/mongodb/eve/
bash start_server.sh
