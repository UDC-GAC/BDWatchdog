#!/usr/bin/env python
from __future__ import print_function

import argparse
import sys
import json

from TimestampsSnitch.src.mongodb.mongodb_agent import MongoDBTimestampAgent


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def print_test(test_data):
    doc_to_dump = {"type": "test", "info": {}}
    for field in ["username", "start_time", "end_time", "experiment_id", "test_id"]:
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
