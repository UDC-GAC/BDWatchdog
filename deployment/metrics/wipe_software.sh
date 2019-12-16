#!/usr/bin/env bash
clean_logs (){
    rm -Rf /var/log/opentsdb/
    rm hadoop-2.9.2/logs/*
    rm hbase-1.4.12/logs/*
}

clean_logs

bash stop.sh
rm -Rf hbase-1.4.12-bin.tar.gz hbase-1.4.12 hadoop-2.9.2 hadoop-2.9.2.tar.gz opentsdb
