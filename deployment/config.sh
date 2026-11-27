#!/usr/bin/env bash

if [ -z "${INSTALLATION_PATH}" ]
then
    INSTALLATION_PATH=${HOME}
fi

if [ -z "${BDWATCHDOG_DATA_DIR}" ]
then
    BDWATCHDOG_DATA_DIR=${INSTALLATION_PATH}/BDWatchdog_data
fi

export DATA_DIR=${BDWATCHDOG_DATA_DIR}/
#export DATA_DIR=/data/0
export BDWATCHDOG_DIR=$(dirname -- "$(dirname -- "$(readlink -f -- "${BASH_SOURCE[0]}")")")
