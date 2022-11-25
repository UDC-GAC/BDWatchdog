#!/usr/bin/env bash
clean_logs (){
    if [ -z ${OPENTSDB_LOG_PATH} ]
    then
        OPENTSDB_LOG_PATH=/var/log/opentsdb/
    fi

    #rm -Rf /var/log/opentsdb/
    rm -Rf ${OPENTSDB_LOG_PATH}
    rm hadoop-2.9.2/logs/*
    rm hbase-1.4.12/logs/*
}

clean_logs

bash stop.sh
rm -Rf hbase-1.4.12-bin.tar.gz hbase-1.4.12 hadoop-2.9.2 hadoop-2.9.2.tar.gz opentsdb
