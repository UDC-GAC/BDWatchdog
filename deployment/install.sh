#!/usr/bin/env bash

setup_ssh () {
    echo -e "\n" | ssh-keygen -b 2048 -t rsa -q -N ""
    echo ""
    cat ${HOME}/.ssh/id_rsa.pub >> ${HOME}/.ssh/authorized_keys
    ssh-keyscan localhost >> ${HOME}/.ssh/known_hosts
    ssh-keyscan 0.0.0.0 >> ${HOME}/.ssh/known_hosts
}

install_dependencies(){
    apt update
    apt install -y python-minimal
    apt install -y python3 python3-pip
    apt install -y mongodb
    apt install -y build-essential
    apt install -y autoconf
    apt install -y gnuplot-x11
    apt install -y apache2

    apt install -y openjdk-8-jdk
    export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
    echo "\
# Add JAVA_HOME
export JAVA_HOME=${JAVA_HOME}
" >> /etc/environment

}

setup_ssh
install_dependencies

source config.sh
mkdir -p ${DATA_DIR}

echo "INSTALLING TIMESTAMPING SERVICE"
cd timestamps
bash install.sh
bash start.sh
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