#!/usr/bin/env bash
# capture CTRL+C, CTRL+Z and quit singles using the trap
trap 'exit' SIGINT
trap 'exit' SIGQUIT
trap 'exit' SIGTSTP


if [ ! -d "$NETHOGS_DIR" ]; then
    echo "Error, nethogs is not installed or its installation directory '$NETHOGS_DIR' is missing, misplaced or badly configured"
    exit 1
fi

if [ ! -d "$NETHOGS_SCRIPTS_DIR" ]; then
    echo "Error, misconfiguration, scripts directory '$NETHOGS_SCRIPTS_DIR' is missing, misplaced or badly configured"
    exit 1
fi


INTERVAL="${1:-5}"
while :
do
    echo "START"
    echo "TIMESTAMP:`date +%s`"
    echo "INTERVAL:$INTERVAL"
    $NETHOGS_DIR/src/nethogs -v 3 -t -d $INTERVAL -c 2 2> /dev/null
    result="$?"
    if [ "$result" -ne 0 ]; then
        echo "Command exited with non-zero status $result"
        exit 1
    fi
    echo "END"
    echo ""
done
