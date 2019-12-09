#!/usr/bin/env bash
cd centos7
bash dependencies/install-dependencies.sh
bash python-dependencies/install-python-dependencies.sh
bash atop/install-atop.sh
bash turbostat/install-turbostat.sh
cd ..

