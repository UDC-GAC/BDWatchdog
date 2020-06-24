#!/usr/bin/env bash
tmux new -s "EVE_FLAME" -d gunicorn3 --bind 0.0.0.0:8001 wsgi:eve_rest -w 4
