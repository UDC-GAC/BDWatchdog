#!/usr/bin/env bash
if [ -z ${JAVA_HOME} ]
then
    echo "\$JAVA_HOME is not set, check the config.sh file and try again"
    exit 0
fi
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

