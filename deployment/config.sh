#!/usr/bin/env bash
export DATA_DIR=${HOME}/BDWatchdog_data/
#export DATA_DIR=/data/0
export BDWATCHDOG_DIR=${HOME}/BDWatchdog/

export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
#export PATH=$PATH:$JAVA_HOME/bin

echo "\

# Add JAVA_HOME
export JAVA_HOME=${JAVA_HOME}
" >> ~/.bashrc
