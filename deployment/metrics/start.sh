#!/usr/bin/env bash
source set_opentsdb_port.sh
if [ -z ${JAVA_HOME} ]
then
    echo "\$JAVA_HOME is not set"
    exit 0
fi
echo "Starting HDFS"
hadoop-2.9.2/sbin/start-dfs.sh
sleep 20

echo "Starting HBase"
hbase-1.4.12/bin/start-hbase.sh
sleep 20

echo "Starting OpenTSDB on port ${OPENTSDB_PORT}"
cd opentsdb
# Keep the port of an already installed OpenTSDB in sync with the current configuration
sed -i -E "s/^tsd\.network\.port[[:space:]]*=.*/tsd.network.port = ${OPENTSDB_PORT}/" opentsdb.conf
tmux new -d -s "OPENTSDB" "./build/tsdb tsd"
cd ..

