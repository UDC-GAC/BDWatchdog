#!/usr/bin/env python
from __future__ import print_function
import sys
import json

from TimestampsSnitch.src.mongodb.mongodb_agent import MongoDBTimestampAgent


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def print_experiment(experiment_data):
    doc_to_dump = {"type": "experiment", "info": {}}
    for field in ["username", "start_time", "end_time", "experiment_id"]:
        if field not in experiment_data:
            eprint("Field {0} missing from experiment {1}".format(field, experiment_data["experiment_id"]))
        else:
            doc_to_dump["info"][field] = experiment_data[field]
    print(json.dumps(doc_to_dump))


if __name__ == '__main__':
    experiment_id = None
    mongodb_agent = MongoDBTimestampAgent()
    if len(sys.argv) < 2:
        eprint("Bad argument, an option is required, an experiment name or 'ALL'")
        exit(1)
    else:
        experiment_id = sys.argv[1]

    if experiment_id == "ALL":
        data = mongodb_agent.get_all_experiments()
        if not data:
            eprint("Couldn't find experiment with id {0}".format(experiment_id))
            exit(0)
    else:
        data = mongodb_agent.get_document(experiment_id, mongodb_agent.get_experiments_endpoint())
        if not data:
            eprint("Couldn't find experiment with id {0}".format(experiment_id))
            exit(0)

    if type(data) == type(dict()):
        print_experiment(data)
    elif type(data) == type(list()):
        for experiment in data:
            print_experiment(experiment)
    else:
        print_experiment(data)
