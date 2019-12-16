#!/usr/bin/env bash
echo "Starting HDFS"
hadoop-2.9.2/sbin/start-dfs.sh
sleep 20

echo "Starting HBase"
hbase-1.4.12/bin/start-hbase.sh
sleep 20

echo "Starting OpenTSDB"
cd opentsdb
tmux new -d -s "OPENTSDB" "./build/tsdb tsd"
cd ..

