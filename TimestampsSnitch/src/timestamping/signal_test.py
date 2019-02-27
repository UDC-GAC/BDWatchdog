#!/usr/bin/env python
from __future__ import print_function

import datetime
import time
import json
import os
import sys
import pwd

from TimestampsSnitch.src.mongodb.mongodb_agent import delete_test_doc


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_username():
    return pwd.getpwuid(os.getuid())[0]


def signal_test(experiment_id, username, test_name):
    d = dict()
    info = dict()
    info["experiment_id"] = experiment_id
    info["username"] = username
    info["test_name"] = test_name
    info["test_id"] = experiment_id + "_" + test_name
    d["info"] = info
    d["type"] = "test"
    return d


def signal_end(experiment_id, username, test_name, timestamp=None):
    d = signal_test(experiment_id, username, test_name)
    if not timestamp:
        timestamp = int(time.time())
    d["info"]["end_time"] = timestamp
    print(json.dumps(d))


def signal_start(experiment_id, username, test_name, timestamp=None):
    d = signal_test(experiment_id, username, test_name)
    if not timestamp:
        timestamp = int(time.time())
    d["info"]["start_time"] = timestamp
    print(json.dumps(d))


if __name__ == '__main__':
    if len(sys.argv) < 4:
        eprint(
            "Some action is required, currently 'start', 'end' and 'delete' are supported, "
            "plus the name of the test, final argument (optional) is time or experiment name if delete")
        exit(1)
    else:
        option = sys.argv[1]
        experiment_name = sys.argv[2]
        test_name = sys.argv[3]
        if option == "start" or option == "end":
            timestamp = None
            if len(sys.argv) >= 5:
                time_str = sys.argv[4]
                t = time_str
                ts = datetime.datetime.strptime(t, "%y/%m/%d %H:%M:%S")
                timestamp = int(time.mktime(ts.timetuple()))

            if option == "start":
                signal_start(experiment_name, get_username(), test_name, timestamp=timestamp)
            elif option == "end":
                signal_end(experiment_name, get_username(), test_name, timestamp=timestamp)
        elif option == "delete":
            delete_test_doc(experiment_name, test_name)
        else:
            eprint("Bad option")
            exit(1)
