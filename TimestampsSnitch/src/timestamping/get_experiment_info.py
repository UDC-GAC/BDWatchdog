#!/usr/bin/env python
from __future__ import print_function
import sys
import os
import json


from TimestampsSnitch.src.mongodb.mongodb_agent import get_document
from TimestampsSnitch.src.mongodb.mongodb_utils import get_all_experiments


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


headers = {'content-type': 'application/json'}

_base_path = os.path.dirname(os.path.abspath(__file__))

default_mongodb_port = 8000
default_mongodb_ip = "mongodb"
default_tests_database_name = "tests"
default_experiments_database_name = "experiments"

MONGODB_IP = "MONGODB_IP"
mongodb_ip = os.getenv(MONGODB_IP, default_mongodb_ip)

MONGODB_PORT = "MONGODB_PORT"
try:
    mongodb_port = str(int(os.getenv(MONGODB_PORT, default_mongodb_port)))
except ValueError:
    eprint("Invalid port configuration, using default '" + str(default_mongodb_port) + "'")
    mongodb_port = str(default_mongodb_port)

TESTS_POST_ENDPOINT = "TESTS_POST_ENDPOINT"
tests_post_endpoint = os.getenv(TESTS_POST_ENDPOINT, default_tests_database_name)

EXPERIMENTS_POST_ENDPOINT = "EXPERIMENTS_POST_ENDPOINT"
experiments_post_endpoint = os.getenv(EXPERIMENTS_POST_ENDPOINT, default_experiments_database_name)

tests_full_endpoint = 'http://' + mongodb_ip + ':' + mongodb_port + '/' + tests_post_endpoint

host_endpoint = 'http://' + mongodb_ip + ':' + mongodb_port
database_name = experiments_post_endpoint

post_doc_buffer_length = 1

MAX_CONNECTION_TRIES = 3

if __name__ == '__main__':
    experiment_id = None

    if len(sys.argv) < 2:
        eprint("Bad argument, an option is required, an experiment name or 'ALL'")
        exit(1)
    else:
        experiment_id = sys.argv[1]

    if experiment_id == "ALL":
        data = get_all_experiments(host_endpoint, database_name)
        if not data:
            eprint("Couldn't find experiment with id {0}".format(experiment_id))
            exit(0)
    else:
        experiments_endpoint = "{0}/{1}".format(host_endpoint, database_name)
        data = get_document(experiment_id, experiments_endpoint)
        if not data:
            eprint("Couldn't find experiment with id {0}".format(experiment_id))
            exit(0)
    if type(data)==type(dict()):
        print(json.dumps(data))
    elif type(data)==type(list()):
        for experiment in data:
            print(json.dumps(experiment))
    else:
        print(json.dumps(data))
