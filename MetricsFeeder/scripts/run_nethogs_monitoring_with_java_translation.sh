#!/usr/bin/env bash
export NETHOGS_DIR="bin-nethogs/"
export TEMPLATE_PATH="src/pipelines/templates/"
export METRICS_PATH="src/pipelines/metrics/"
export TAGS_PATH="src/pipelines/tags/"
export NETHOGS_SCRIPTS_DIR="src/nethogs"

export PYTHONUNBUFFERED="yes"
export POST_DOC_BUFFER_TIMEOUT=5
export NETHOGS_SAMPLING_FREQUENCY=5
export JAVA_TRANSLATOR_MAX_TRIES=2
export JAVA_TRANSLATOR_WAIT_TIME=3

if [ ! -d "$NETHOGS_DIR" ]; then
    echo "Error, nethogs is not installed or its installation directory '$NETHOGS_DIR' is missing, misplaced or badly configured"
    exit 1
fi

tmux new -s "NETHOGS" "bash ./src/nethogs/run_nethogs.sh $NETHOGS_SAMPLING_FREQUENCY | python3 ./src/nethogs/filter_raw_output.py | python3 ./src/nethogs/nethogs_to_json_with_java_translation.py | python3 ./src/pipelines/send_to_OpenTSDB.py"


