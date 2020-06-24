#!/usr/bin/env bash
tmux new -s "EVE" -d gunicorn --bind 0.0.0.0:500 wsgi:eve_rest -w 4
