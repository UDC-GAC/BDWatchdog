#!/usr/bin/env python
from __future__ import print_function
import time
import json
import os
import sys
import pwd


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


default_experiment_id = "experiment_0"


def get_username():
    return pwd.getpwuid(os.getuid())[0]


def signal_end(experiment_id, username):
    d = dict()

    info = dict()
    info["experiment_id"] = experiment_id
    info["username"] = username
    info["end_time"] = int(time.time())

    d["info"] = info
    d["type"] = "experiment"

    print(json.dumps(d))


def signal_start(experiment_id, username):
    d = dict()

    info = dict()
    info["experiment_id"] = experiment_id
    info["username"] = username
    info["start_time"] = int(time.time())

    d["info"] = info
    d["type"] = "experiment"

    print(json.dumps(d))


if __name__ == '__main__':
    if len(sys.argv) < 3:
        eprint("Some action is required, currently 'start' and 'end' are supported, plus the experiment_name")
        exit(1)
    else:
        option = sys.argv[1]
        experiment_id = sys.argv[2]
        if option == "start":
            signal_start(experiment_id, get_username())
        elif option == "end":
            signal_end(experiment_id, get_username())
        else:
            eprint("Bad option")
            exit(1)
