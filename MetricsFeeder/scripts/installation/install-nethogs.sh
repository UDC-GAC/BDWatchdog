#!/usr/bin/env bash
sudo apt-get install libpcap-dev
git clone https://github.com/raboof/nethogs bin-nethogs
cd bin-nethogs
make
cd ..
sudo setcap "cap_net_admin,cap_net_raw=ep" bin-nethogs/src/nethogs
