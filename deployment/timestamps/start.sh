#!/usr/bin/env bash
systemctl restart mongodb
cd ${BDWATCHDOG_DIR}/TimestampsSnitch/src/mongodb/eve/
bash start_server.sh
