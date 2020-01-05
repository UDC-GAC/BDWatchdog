#!/usr/bin/env bash
#pdoc3 --html --template-dir code/templates/ --force ../MetricsFeeder/src -o code

source /home/jonatan/development/BDWatchdog/set_pythonpath.sh

pdoc3 --html --template-dir templates/ --force ../MetricsFeeder/src/ -o code/MetricsFeeder
cp templates/index.html code/index.html
