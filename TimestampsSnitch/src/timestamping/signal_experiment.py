#!/usr/bin/env python
from __future__ import print_function
import time
import json
import os
import sys
import pwd

from TimestampsSnitch.src.mongodb.mongodb_agent import MongoDBTimestampAgent

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_username():
    return pwd.getpwuid(os.getuid())[0]


def signal_experiment(experiment_id, username):
    d = dict()
    info = dict()
    info["experiment_id"] = experiment_id
    info["username"] = username
    d["info"] = info
    d["type"] = "experiment"
    return d


def signal_end(experiment_id, username):
    d = signal_experiment(experiment_id, username)
    d["info"]["end_time"] = int(time.time())
    print(json.dumps(d))


def signal_start(experiment_id, username):
    d = signal_experiment(experiment_id, username)
    d["info"]["start_time"] = int(time.time())
    print(json.dumps(d))


if __name__ == '__main__':
    mongodb_agent = MongoDBTimestampAgent()
    if len(sys.argv) < 3:
        eprint("Some action is required, currently 'start', 'end' and 'delete' are supported, plus the experiment_name")
        exit(1)
    else:
        option = sys.argv[1]
        experiment_id = sys.argv[2]
        if option == "start":
            signal_start(experiment_id, get_username())
        elif option == "end":
            signal_end(experiment_id, get_username())
        elif option == "delete":
            mongodb_agent.delete_experiment(experiment_id)
        else:
            eprint("Bad option")
            exit(1)
