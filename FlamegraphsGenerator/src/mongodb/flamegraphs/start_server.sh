#!/usr/bin/env bash
tmux new -s "FLAME" -d gunicorn --bind 0.0.0.0:5001 wsgi:app -w 4
