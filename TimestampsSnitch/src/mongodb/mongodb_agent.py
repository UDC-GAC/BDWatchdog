#!/usr/bin/env python
from __future__ import print_function
import sys
import time
import requests
import json
import ast
import os


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


headers = {'content-type': 'application/json'}

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
experiments_full_endpoint = 'http://' + mongodb_ip + ':' + mongodb_port + '/' + experiments_post_endpoint

post_doc_buffer_length = 1

MAX_CONNECTION_TRIES = 3


def get_test_by_name(experiment_name, test_name):
    query = '?where={%22experiment_id%22: %22' + experiment_name + '%22, %22test_name%22:%22' + test_name + '%22}'
    tests_full_endpoint = "http://mongodb:8000/tests/" + query
    tries = 0
    while tries <= MAX_CONNECTION_TRIES:
        status_code = None
        try:
            r = requests.get(tests_full_endpoint)
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 404:
                return {}
            else:
                status_code = r.status_code
        except requests.ConnectionError as e:
            eprint("Error with request {0}".format(str(e)))
        eprint("Couldn't get document {0}, trying again for the {1} time out of {2}".format(
            test_name, tries, MAX_CONNECTION_TRIES))
        if status_code:
            eprint("Status code was {0}".format(str(status_code)))
        tries += 1

    if tries > MAX_CONNECTION_TRIES:
        error_string = "Information retrieval for document {0} failed too many times, aborting".format(doc_id)
        eprint(error_string)
        raise requests.ConnectionError(error_string)


def get_document(doc_id, endpoint):
    tries = 0
    while tries <= MAX_CONNECTION_TRIES:
        status_code = None
        try:
            r = requests.get("{0}/{1}".format(endpoint, str(doc_id)))
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 404:
                return {}
            else:
                status_code = r.status_code
        except requests.ConnectionError as e:
            eprint("Error with request {0}".format(str(e)))
        eprint("Couldn't get document {0}, trying again for the {1} time out of {2}".format(
            doc_id, tries, MAX_CONNECTION_TRIES))
        if status_code:
            eprint("Status code was {0}".format(str(status_code)))
        tries += 1

    if tries > MAX_CONNECTION_TRIES:
        error_string = "Information retrieval for document {0} failed too many times, aborting".format(doc_id)
        eprint(error_string)
        raise requests.ConnectionError(error_string)


def merge_data_from_existing_doc(old, new):
    try:
        if "start_time" not in new.keys():
            new["start_time"] = old["start_time"]
    except KeyError:
        pass

    try:
        if "end_time" not in new.keys():
            new["end_time"] = old["end_time"]
    except KeyError:
        pass

    return new


def post_doc(doc, info, endpoint):
    tries = 0
    while tries <= MAX_CONNECTION_TRIES:
        if info == {}:
            # Document doesn't exist, create
            r = requests.post(endpoint, headers=headers, data=json.dumps(doc))
            if r.status_code != 201:
                eprint(
                    "[SNITCH MONGODB AGENT] couldn't properly post documents to address " + endpoint)
                eprint(r.text)
            else:
                print(
                    "Document created at: " + time.strftime("%D %H:%M:%S", time.localtime()) + " timestamp is " + str(
                        time.time()))
                break
        else:
            # Test exists, update
            etag = info["_etag"]
            doc_id = info["_id"]

            doc = merge_data_from_existing_doc(info, doc)

            these_headers = headers
            these_headers["If-Match"] = etag
            r = requests.put(endpoint + "/" + str(doc_id), headers=these_headers,
                             data=json.dumps(doc))
            if r.status_code != 200:
                eprint("[SNITCH MONGODB AGENT] couldn't properly put document to address " + endpoint)
                eprint(r.text)
            else:
                print(
                    "Document updated at: " + time.strftime("%D %H:%M:%S", time.localtime()) + " timestamp is " + str(
                        time.time()))
                break
    if tries > MAX_CONNECTION_TRIES:
        error_string = "Information posting for document {0} failed too many times, aborting".format(str(doc))
        eprint(error_string)
        raise ConnectionError(error_string)


def experiment_exists(experiment_id):
    info = get_document(experiment_id, experiments_full_endpoint)
    if info:
        return True
    return False


def send_experiment_docs(documents):
    for experiment in documents:
        eprint("Retrieving experiment {0}".format(experiment["experiment_id"]))
        info = get_document(experiment["experiment_id"], experiments_full_endpoint)
        post_doc(experiment, info, experiments_full_endpoint)


def send_test_docs(docs):
    for test in docs:
        if not experiment_exists(test["experiment_id"]):
            # Experiment doesn't exist
            eprint("[SNITCH MONGODB AGENT] couldn't properly post documents to address " + experiments_full_endpoint)
            eprint("[SNITCH MONGODB AGENT] experiment " + test["experiment_id"] + " doesn't exist")
            continue
        info = get_document(test["test_id"], tests_full_endpoint)
        post_doc(test, info, tests_full_endpoint)


def send_docs(documents):
    if len(documents["experiment"]) >= 1:
        send_experiment_docs(documents["experiment"])
    if len(documents["test"]) >= 1:
        send_test_docs(documents["test"])


def get_legth_docs(documents):
    l = 0
    for key in documents:
        l += len(documents[key])
    return l


def delete_test_doc(experiment_id, test_id):
    if experiment_exists(experiment_id):
        test = get_test_by_name(experiment_id, test_id)["_items"]
        if not test:
            print("Document doesn't {0} exist".format(test_id))
            return
        test = test[0]
        headers["If-Match"] = test["_etag"]
        tests_full_endpoint = "http://mongodb:8000/tests/" + test["_id"]
        r = requests.delete(tests_full_endpoint, headers=headers)
        if r.status_code != 204:
            eprint(
                "[SNITCH MONGODB AGENT] couldn't properly delete document to address " + tests_full_endpoint)
            eprint(r.text)
        else:
            print("Document deleted at: " + time.strftime("%D %H:%M:%S", time.localtime()))
    else:
        return False


if __name__ == '__main__':
    abort = False

    docs = dict()
    docs["experiment"] = []
    docs["test"] = []

    eprint("[SNITCH MONGODB AGENT] Mongodb agent started, waiting for input to send.")
    eprint("[SNITCH MONGODB AGENT] Endpoints to use will be '" + str(
        experiments_full_endpoint) + "' to experiments and '" + str(tests_full_endpoint) + "' to tests")

    try:
        # UNAFFECTED BY BUFFERING
        while True:
            line = sys.stdin.readline()

            if line == "":
                # Reached EOF
                break

            try:
                new_doc = ast.literal_eval(line)
                docs[new_doc["type"]] = docs[new_doc["type"]] + [new_doc["info"]]
            except ValueError:
                print("Error with document " + str(line))
                continue

            length_docs = get_legth_docs(docs)
            if length_docs >= post_doc_buffer_length:
                send_docs(docs)
                docs = dict()
                docs["experiment"] = []
                docs["test"] = []

                if abort:
                    exit(1)
                sys.stdout.flush()
        send_docs(docs)
    except IOError as e:
        eprint("[SNITCH MONGODB AGENT] terminated")
        eprint(e)
    except KeyboardInterrupt:
        eprint("[SNITCH MONGODB AGENT] terminated")
        send_docs(docs)
