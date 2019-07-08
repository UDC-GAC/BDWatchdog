#!/usr/bin/env python
from __future__ import print_function

import argparse
import datetime
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


def signal_experiment(experiment_id, username, time_signal_field, timestamp):
    d = dict()
    info = dict()
    info["experiment_id"] = experiment_id
    info["username"] = username
    d["info"] = info
    d["type"] = "experiment"
    d["info"]["{0}_time".format(time_signal_field)] = timestamp
    print(json.dumps(d))


if __name__ == '__main__':
    mongodb_agent = MongoDBTimestampAgent()

    parser = argparse.ArgumentParser(description='Signal for the start, end times or for the deletion of a test.')
    parser.add_argument('option', metavar='option', type=str,
                        help='an operation option "start", "end" or "delete"')
    parser.add_argument('experiment_name', metavar='experiment_name', type=str,
                        help='The name of the experiment that encompasses this test')
    parser.add_argument('--time', type=str, default=None,
                        help="A time string in the form 'yy/mm/dd HH:MM:SS'")
    args = parser.parse_args()

    timestamp = None
    if args.time:
        try:
            ts = datetime.datetime.strptime(args.time, "%y/%m/%d %H:%M:%S")
            timestamp = int(time.mktime(ts.timetuple()))
        except ValueError:
            eprint("Bad time format, it should follow the format 'yy/mm/dd HH:MM:SS' (e.g., '18/06/01 12:34:36')")
            exit(1)
    else:
        timestamp = int(time.time())


    if args.option == "start" or args.option == "end":
        signal_experiment(args.experiment_name, get_username(), args.option, timestamp)
    elif args.option == "delete":
        mongodb_agent.delete_experiment(args.experiment_name)
    else:
        eprint("Bad option")
        exit(1)
