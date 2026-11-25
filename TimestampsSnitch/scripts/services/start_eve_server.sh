#!/usr/bin/env bash

scriptDir=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")
SERVICES_CONFIG_FILE="${scriptDir}/../../../services_config.yml"

# Port priority: EVE_SERVER_PORT environment variable > services_config.yml > 8000
if [ -z "${EVE_SERVER_PORT}" ]; then
    EVE_SERVER_PORT=$(grep -E '^[[:space:]]*EVE_SERVER_PORT[[:space:]]*:' "${SERVICES_CONFIG_FILE}" 2>/dev/null \
        | head -n 1 | cut -d ':' -f 2 | cut -d '#' -f 1 | tr -d "[:space:]\"'")
fi
EVE_SERVER_PORT=${EVE_SERVER_PORT:-8000}

cd $scriptDir/../../src/mongodb/eve && gunicorn3 --bind 0.0.0.0:${EVE_SERVER_PORT} wsgi:eve_rest -w 2
