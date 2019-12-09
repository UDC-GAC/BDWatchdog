#!/usr/bin/env bash
cd ubuntu
#bash python-dependencies/install-python-dependencies.sh
bash atop/install-atop.sh
#bash atop/install-netatop.sh
bash turbostat/install-turbostat.sh
cd ..
