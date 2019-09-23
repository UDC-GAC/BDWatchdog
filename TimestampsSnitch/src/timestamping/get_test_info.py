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

import argparse
import sys
import json

from TimestampsSnitch.src.mongodb.mongodb_agent import MongoDBTimestampAgent


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def print_test(test_data):
    doc_to_dump = {"type": "test", "info": {}}
    for field in ["username", "start_time", "end_time", "experiment_id", "test_id", "test_name"]:
        if field not in test_data:
            eprint("Field {0} missing from test {1}".format(field, test_data["test_id"]))
        else:
            doc_to_dump["info"][field] = test_data[field]
    print(json.dumps(doc_to_dump))


if __name__ == '__main__':
    mongodb_agent = MongoDBTimestampAgent()

    parser = argparse.ArgumentParser(description='Get test information of a particular experiment')
    parser.add_argument('experiment_name', metavar='experiment_name', type=str,
                        help='The name of the experiment that hosts the test')
    parser.add_argument('--test', type=str, default=None,
                        help='The name of the test, otherwise all will be retrieved')

    args = parser.parse_args()

    if args.test:
        tests = list(mongodb_agent.get_test(args.experiment_name, args.test))
    else:
        tests = mongodb_agent.get_experiment_tests(args.experiment_name)

    if not tests:
        eprint("Couldn't find experiment with id {0}".format(args.experiment_name))
        exit(0)
    for test in tests:
        print_test(test)
