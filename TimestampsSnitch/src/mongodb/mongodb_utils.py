# !/usr/bin/env python
from __future__ import print_function

import sys
import requests


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_all_experiments(host_endpoint, database_name):
    last_page = False
    all_experiments = list()
    endpoint = "{0}/{1}".format(host_endpoint, database_name)
    while not last_page:
        data = get_experiments(endpoint)
        if not data:
            return all_experiments
        num_page = data["_meta"]["page"]
        max_num_retrieved_experiments = num_page * data["_meta"]["max_results"]
        num_total_experiments = data["_meta"]["total"]
        if max_num_retrieved_experiments < num_total_experiments:
            endpoint = "{0}/{1}".format(host_endpoint, data["_links"]["next"]["href"])
        else:
            last_page = True
        all_experiments += data["_items"]
    return all_experiments


def get_experiments(endpoint):
    try:
        r = requests.get(endpoint)
        return r.json()
    except requests.ConnectionError as e:
        eprint("Error with request {0}".format(str(e)))
        return None


def get_experiment_tests(experiment_id, mongodb_address, endpoint, tests=list()):
    try:
        r = requests.get(endpoint)
    except requests.ConnectionError as e:
        eprint("Error with request {0}".format(str(e)))
        return None

    response = r.json()
    tests = tests + response["_items"]
    max_results_per_page = response["_meta"]["max_results"]
    num_page = response["_meta"]["page"]
    total_docs = response["_meta"]["total"]

    if max_results_per_page * num_page < total_docs:
        # Still documents to retrieve in next page
        next_endpoint = 'http://{0}/{1}'.format(mongodb_address, response["_links"]["next"]["href"])
        return get_experiment_tests(experiment_id, mongodb_address, next_endpoint, tests=tests)
    else:
        return tests
