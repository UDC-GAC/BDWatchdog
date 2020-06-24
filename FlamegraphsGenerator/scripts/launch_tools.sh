#!/usr/bin/env bash
tmux new -d -s map "bash map.sh 10"
tmux new -d -s profile "bash profile.sh 10 203"
tmux new -d -s send "source ../../set_pythonpath.sh; bash send.sh 20"
