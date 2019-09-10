# Copyright (c) 2019 Universidade da Coruña
# Authors:
#     - Jonatan Enes [main](jonatan.enes@udc.es, jonatan.enes.alvarez@gmail.com)
#     - Roberto R. Expósito
#     - Juan Touriño
#
# This file is part of the ServerlessContainers framework, from
# now on referred to as ServerlessContainers.
#
# ServerlessContainers is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# ServerlessContainers is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ServerlessContainers. If not, see <http://www.gnu.org/licenses/>.


from __future__ import print_function

import datetime
import time
import json
import os
import sys
import pwd
import argparse

from TimestampsSnitch.src.mongodb.mongodb_agent import MongoDBTimestampAgent


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_username():
    return pwd.getpwuid(os.getuid())[0]


def signal_test(experiment_id, username, test_name, timestamp, time_signal_field, tags=None):
    d = dict()
    info = dict()
    info["experiment_id"] = experiment_id
    info["username"] = username
    info["test_name"] = test_name
    info["test_id"] = experiment_id + "_" + test_name
    if tags:
        info["tags"] = tags
    d["info"] = info
    d["type"] = "test"
    if not timestamp:
        timestamp = int(time.time())
    d["info"]["{0}_time".format(time_signal_field)] = timestamp
    print(json.dumps(d))

if __name__ == '__main__':
    mongodb_agent = MongoDBTimestampAgent()

    parser = argparse.ArgumentParser(description='Signal for the start, end times or for the deletion of a test.')
    parser.add_argument('option', metavar='option', type=str,
                        help='an operation option "start", "end" or "delete"')
    parser.add_argument('experiment_name', metavar='experiment_name', type=str,
                        help='The name of the experiment that encompasses this test')
    parser.add_argument('test_name', metavar='test_name', type=str,
                        help='The name of the test')
    parser.add_argument('--time', type=str, default=None,
                        help="A time string in the form 'yy/mm/dd HH:MM:SS'")
    parser.add_argument('--tags', type=str, default=None, nargs='+',
                        help="A list of tags")

    args = parser.parse_args()

    if args.option == "start" or args.option == "end":
        timestamp = None
        if args.time:
            try:
                ts = datetime.datetime.strptime(args.time, "%y/%m/%d %H:%M:%S")
                timestamp = int(time.mktime(ts.timetuple()))
            except ValueError:
                eprint("Bad time format, it should follow the format 'yy/mm/dd HH:MM:SS' (e.g., '18/06/01 12:34:36')")
                exit(1)
        else:
            timestamp = args.time

        signal_test(args.experiment_name, get_username(), args.test_name, timestamp, args.option, args.tags)
    elif args.option == "delete":
        mongodb_agent.delete_test(args.experiment_name, args.test_name)
    else:
        eprint("Bad option")
        exit(1)
