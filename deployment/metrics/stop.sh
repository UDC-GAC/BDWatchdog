#!/usr/bin/env bash
echo "Stopping OpenTSDB"
tmux kill-session -t OPENTSDB

echo "Stopping HBase"
hbase-1.4.12/bin/stop-hbase.sh

echo "Stopping HDFS"
hadoop-2.9.2/sbin/stop-dfs.sh
