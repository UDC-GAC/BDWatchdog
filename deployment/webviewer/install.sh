#!/usr/bin/env bash

if [ -z ${BDWATCHDOG_DIR} ]
then
    echo "\$BDWATCHDOG_DIR is not set, check and source the config.sh file and try again"
    exit 0
fi

## With copy
cp -R ${BDWATCHDOG_DIR}/TimeseriesViewer/* /var/www/html/

## With Symbolic Link
#cd /var/www/html
#ln -s ${BDWATCHDOG_DIR}/TimeseriesViewer/src/ bdwatchdog-viewer
#chmod o+x ${BDWATCHDOG_DIR}

cd ${BDWATCHDOG_DIR}