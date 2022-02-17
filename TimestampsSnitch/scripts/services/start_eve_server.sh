#!/usr/bin/env bash

scriptDir=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")

cd $scriptDir/../../src/mongodb/eve && gunicorn3 --bind 0.0.0.0:8000 wsgi:eve_rest -w 2
