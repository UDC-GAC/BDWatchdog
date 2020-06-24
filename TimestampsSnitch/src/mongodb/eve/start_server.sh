#!/usr/bin/env bash
tmux new -s "EVE_TIMES" -d gunicorn3 --bind 0.0.0.0:8000 wsgi:eve_rest -w 2
