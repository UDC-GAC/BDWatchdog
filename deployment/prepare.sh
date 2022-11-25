setup_ssh () {
    echo -e "\n" | ssh-keygen -b 2048 -t rsa -q -N "" -f ${HOME}/.ssh/id_rsa
    echo ""
    cat ${HOME}/.ssh/id_rsa.pub >> ${HOME}/.ssh/authorized_keys
    ssh-keyscan localhost >> ${HOME}/.ssh/known_hosts
    ssh-keyscan 0.0.0.0 >> ${HOME}/.ssh/known_hosts
}

## Added by Oscar
setup_ssh_root () {
    cat ${HOME}/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys
    ssh-keyscan localhost >> /root/.ssh/known_hosts
    ssh-keyscan 0.0.0.0 >> /root/.ssh/known_hosts
}

# TODO
# Here it should be checked if the /etc/environment file already hast the JAVA_HOME variable set
install_dependencies(){
    apt update
    apt install -y python2-minimal
    apt install -y python3 python3-pip python-is-python3
    apt install -y build-essential
    apt install -y autoconf
    apt install -y gnuplot-x11

    apt install -y openjdk-8-jdk
    export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
    echo "\
# Add JAVA_HOME
export JAVA_HOME=${JAVA_HOME}
" >> /etc/environment

}

setup_ssh

if [ -n "$1" ] && [ "$1" == "ssh_setup" ]
then
    # only execute the ssh_setup
    exit 0
fi

## Added by Oscar
setup_ssh_root

install_dependencies
source /etc/environment
