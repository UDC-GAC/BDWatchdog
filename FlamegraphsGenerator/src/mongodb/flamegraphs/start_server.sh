#!/usr/bin/env bash
tmux new -s "FLAME" -d gunicorn3 --bind 0.0.0.0:8002 wsgi:app -w 4
