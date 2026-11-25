#!/usr/bin/env bash
# Sourced by install.sh and start.sh to set the port of the OpenTSDB server (TSD)
# Port priority: OPENTSDB_PORT environment variable > OPENTSDB_PORT in BDWatchdog's services_config.yml > 4242
if [ -z "${OPENTSDB_PORT}" ]; then
    OPENTSDB_PORT=$(grep -E '^[[:space:]]*OPENTSDB_PORT[[:space:]]*:' "$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")/../../services_config.yml" 2>/dev/null \
        | head -n 1 | cut -d ':' -f 2 | cut -d '#' -f 1 | tr -d "[:space:]\"'")
fi
export OPENTSDB_PORT=${OPENTSDB_PORT:-4242}
