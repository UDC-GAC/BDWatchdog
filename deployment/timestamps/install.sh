#!/usr/bin/env bash
source ../config.sh
if [ -z ${BDWATCHDOG_DIR} ]
then
    echo "\$BDWATCHDOG_DIR is not set, check and source the config.sh file and try again"
    exit 0
fi

apt install -y mongodb
apt install -y gunicorn

pip3 install -r requirements.txt
