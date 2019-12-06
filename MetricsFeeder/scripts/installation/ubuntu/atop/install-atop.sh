#!/usr/bin/env bash

# Install atop dependencies
# Dependencies like make and a C compiler are still needed but omitted here
sudo apt install -y libz-dev
sudo apt install -y libncurses5-dev libncursesw5-dev

# Download and uncompress
wget http://www.atoptool.nl/download/atop-2.3.0.tar.gz
tar xvf atop-2.3.0.tar.gz
cd atop-2.3.0/

# Compile and install
sudo make systemdinstall

# Return
cd ..

# Clean
rm -R atop-2.3.0.tar.gz
sudo rm -Rf atop-2.3.0
