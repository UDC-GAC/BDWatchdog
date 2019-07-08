#!/usr/bin/env bash
KERNEL_VERSION=`uname -r`

# Install turbostat
	sudo apt install -y linux-tools-$KERNEL_VERSION
	sudo apt install -y linux-cloud-tools-$KERNEL_VERSION
	sudo apt install -y linux-tools-generic
	sudo apt install -y linux-cloud-tools-generic
	
