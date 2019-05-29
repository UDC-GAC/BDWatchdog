#!/usr/bin/env python
from __future__ import print_function
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
    experiment_id = None
    mongodb_agent = MongoDBTimestampAgent()
    if len(sys.argv) < 3:
        eprint("Bad argument, both an experiment and a test name are required")
        exit(1)
    else:
        experiment_id = sys.argv[1]
        test_id = sys.argv[2]

        data = mongodb_agent.get_test_by_name(experiment_id, test_id)
        if not data:
            eprint("Couldn't find experiment with id {0}".format(experiment_id))
            exit(0)
        print_test(data)
