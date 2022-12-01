#!/usr/bin/env bash

if [ -z ${INSTALLATION_PATH} ]
then
    INSTALLATION_PATH=${HOME}
fi

export DATA_DIR=${INSTALLATION_PATH}/BDWatchdog_data/
#export DATA_DIR=/data/0
export BDWATCHDOG_DIR=${INSTALLATION_PATH}/BDWatchdog/

