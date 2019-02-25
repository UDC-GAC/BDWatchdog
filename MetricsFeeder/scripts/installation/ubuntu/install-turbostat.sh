#!/usr/bin/env bash
KERNEL_VERSION=`uname -r`

# Install turbostat
	sudo apt install linux-tools-$KERNEL_VERSION
	sudo apt install linux-cloud-tools-$KERNEL_VERSION
	sudo apt install linux-tools-generic
	sudo apt install linux-cloud-tools-generic
	
