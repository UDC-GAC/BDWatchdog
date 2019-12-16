#!/usr/bin/env bash

if [ -z ${BDWATCHDOG_DIR} ]
then
    echo "\$BDWATCHDOG_DIR is not set, check and source the config.sh file and try again"
    exit 0
fi
cd /var/log/html
ln -s ${BDWATCHDOG_DIR}/TimeseriesViewer/src/ bdwatchdog-viewer
cd ${BDWATCHDOG_DIR}