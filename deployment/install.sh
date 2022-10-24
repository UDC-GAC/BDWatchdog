#!/usr/bin/env bash

bash prepare.sh

source config.sh
mkdir -p ${DATA_DIR}

echo "INSTALLING TIMESTAMPING SERVICE"
cd timestamps
bash install.sh
#bash start.sh
#echo "going to test it now"
sleep 5
#bash test.sh
cd ..

echo "INSTALLING OPENTSDB SERVICE"
cd metrics
bash install.sh
bash start.sh
cd ..

echo "INSTALLING WEB SERVER"
cd webviewer
bash install.sh
bash start.sh
cd ..
