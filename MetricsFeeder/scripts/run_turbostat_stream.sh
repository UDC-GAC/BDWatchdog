#!/usr/bin/env bash
export PYTHONUNBUFFERED="yes"
export POST_DOC_BUFFER_TIMEOUT=10
export TURBOSTAT_SAMPLING_FREQUENCY=3
#export POST_DOC_BUFFER_LENGTH=10

source ../set_pythonpath.sh

# The extra PYTHONUNBUFFERED is a fix for the G5000 infrastructure experiments where I do not known if I do not use it the python output is buffered
turbostat --debug -i $TURBOSTAT_SAMPLING_FREQUENCY 2>/dev/null \
| sed -u -e 's/^[ \t]*//' | sed -u -e 's/[[:space:]]\+/,/g' \
| python3 ./src/turbostat/turbostat_to_json.py \
| python3 ./src/pipelines/send_to_OpenTSDB.py
