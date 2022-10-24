#!/usr/bin/env bash
source ../config.sh
if [ -z ${BDWATCHDOG_DIR} ]
then
    echo "\$BDWATCHDOG_DIR is not set, check and source the config.sh file and try again"
    exit 0
fi
#systemctl restart mongodb
bash ${BDWATCHDOG_DIR}/TimestampsSnitch/scripts/services/start_eve_server_tmux.sh
