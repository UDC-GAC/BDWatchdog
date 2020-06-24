#!/usr/bin/env bash
tmux new -s "EVE_FLAME" -d gunicorn --bind 0.0.0.0:5000 wsgi:eve_rest -w 4
