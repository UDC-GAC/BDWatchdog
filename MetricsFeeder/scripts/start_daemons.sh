#!/usr/bin/env bash
source ../../set_pythonpath.sh
python src/daemons/atop.py start
python src/daemons/nethogs.py start