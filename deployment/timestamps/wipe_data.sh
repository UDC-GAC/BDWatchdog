#!/usr/bin/env bash
function wipe () {

tmux kill-session -t EVE
systemctl start mongodb
mongo << EOF
use timestamping
db.experiments.drop()
db.tests.drop()
EOF

}

echo "This script will wipe all of the timestamping information"
read -p "Are you sure (y/n)? " choice
case "$choice" in 
  y|Y ) echo "yes";;
  n|N ) echo "no";;
  * ) echo "invalid";;
esac

if [ "$choice" = "y" ]; then
	wipe;	
fi
