#!/usr/bin/env bash
KERNEL_VERSION=`uname -r`

# Install turbostat
	sudo yum install -y kernel-tools-$KERNEL_VERSION
	sudo yum install -y kernel-debug-devel-$KERNEL_VERSION
	sudo yum install -y kernel-devel-$KERNEL_VERSION

