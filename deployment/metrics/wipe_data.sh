#!/usr/bin/env bash
function wipe_data () {
	rm -Rf ${DATA_DIR}/*
}

source ../config.sh

if [ -z ${DATA_DIR} ]
then
    echo "\$DATA_DIR is empty, check and source the config.sh file and try again"
    exit 0
fi


echo "This script will wipe all of the timeseries data"
read -p "Are you sure (y/n)? " choice
case "$choice" in
  y|Y ) echo "yes";;
  n|N ) echo "no";;
  * ) echo "invalid";;
esac

if [ "$choice" = "y" ]; then
        wipe_data;
fi
