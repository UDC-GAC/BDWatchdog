#!/usr/bin/env bash
# Install atop

	# Install atop dependencies
		# Dependencies like make and a C compiler are still needed but omitted here
		yum install -y zlib-devel
		yum install -y ncurses ncurses-devel

	# Download and uncompress
		wget http://www.atoptool.nl/download/atop-2.3.0.tar.gz
		tar xvf atop-2.3.0.tar.gz
		cd atop-2.3.0/
	
	# Compile and install
		make systemdinstall
	
	# Return 
		cd ..

	# Clean
		rm -R atop-2.3.0.tar.gz
		rm -Rf atop-2.3.0
