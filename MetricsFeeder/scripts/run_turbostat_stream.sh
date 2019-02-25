#!/usr/bin/env bash
export PYTHONUNBUFFERED="yes"
export POST_DOC_BUFFER_TIMEOUT=10
export TURBOSTAT_SAMPLING_FREQUENCY=5

tmux new -s "TURBOSTAT" "turbostat -i $TURBOSTAT_SAMPLING_FREQUENCY 2>/dev/null \
| sed -u -e 's/^[ \t]*//' | sed -u -e 's/[[:space:]]\+/,/g' \
| ./src/turbostat/turbostat_to_csv.py | ./src/pipelines/csv_to_json.py | ./src/pipelines/json_to_TSDB_json.py \
| ./src/pipelines/send_to_OpenTSDB.py"
