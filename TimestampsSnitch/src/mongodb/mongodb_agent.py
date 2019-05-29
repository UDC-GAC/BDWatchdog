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

post_doc_buffer_length = 1
MAX_CONNECTION_TRIES = 3


class MongoDBTimestampAgent:
    def __init__(self):
        self.tests_full_endpoint = "http://{0}:{1}/{2}".format(mongodb_ip, mongodb_port, tests_post_endpoint)
        self.experiments_full_endpoint = "http://{0}:{1}/{2}".format(mongodb_ip, mongodb_port,
                                                                     experiments_post_endpoint)

    def get_experiments_endpoint(self):
        return self.experiments_full_endpoint

    def get_tests_endpoint(self):
        return self.tests_full_endpoint

    def get_test_by_name(self, experiment_name, test_name):
        query = '?where={%22experiment_id%22: %22' + experiment_name + '%22, %22test_name%22:%22' + test_name + '%22}'
        endpoint = "{0}/{1}".format(self.tests_full_endpoint, query)
        tries = 0
        while tries <= MAX_CONNECTION_TRIES:
            status_code = None
            try:
                r = requests.get(endpoint)
                if r.status_code == 200:
                    tests = r.json()["_items"]
                    if tests:
                        return r.json()["_items"][0]
                    else:
                        return []
                elif r.status_code == 404:
                    return {}
                else:
                    status_code = r.status_code
            except requests.ConnectionError as error:
                eprint("Error with request {0}".format(str(error)))
            eprint("Couldn't get document {0}, trying again for the {1} time out of {2}".format(
                test_name, tries, MAX_CONNECTION_TRIES))
            if status_code:
                eprint("Status code was {0}".format(str(status_code)))
            tries += 1

        if tries > MAX_CONNECTION_TRIES:
            error_string = "Information retrieval for document {0} failed too many times, aborting"
            eprint(error_string)
            raise requests.ConnectionError(error_string)

    @staticmethod
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
            except requests.ConnectionError as error:
                eprint("Error with request {0}".format(str(error)))
            eprint("Couldn't get document {0}, trying again for the {1} time out of {2}".format(
                doc_id, tries, MAX_CONNECTION_TRIES))
            if status_code:
                eprint("Status code was {0}".format(str(status_code)))
            tries += 1

        if tries > MAX_CONNECTION_TRIES:
            error_string = "Information retrieval for document {0} failed too many times, aborting".format(doc_id)
            eprint(error_string)
            raise requests.ConnectionError(error_string)

    @staticmethod
    def merge_data_from_existing_doc(old, new):
        for key in ["start_time", "end_time"]:
            try:
                if key not in new.keys():
                    new[key] = old[key]
            except KeyError:
                pass

        return new

    def post_doc(self, doc, info, endpoint):
        tries = 0
        while tries <= MAX_CONNECTION_TRIES:
            if info == {}:
                # Document doesn't exist, create
                r = requests.post(endpoint, headers=headers, data=json.dumps(doc))
                if r.status_code != 201:
                    eprint("[MONGODB AGENT] couldn't properly put document to address {0}".format(endpoint))
                    eprint(r.text)
                else:
                    print("Document created at: {0}".format(
                        time.strftime("%D %H:%M:%S", time.localtime()) + " timestamp is " + str(time.time())))
                    break
            else:
                # Test exists, update
                etag = info["_etag"]
                doc_id = info["_id"]

                doc = self.merge_data_from_existing_doc(info, doc)

                these_headers = headers
                these_headers["If-Match"] = etag
                r = requests.put(endpoint + "/" + str(doc_id), headers=these_headers,
                                 data=json.dumps(doc))
                if r.status_code != 200:
                    eprint("[MONGODB AGENT] couldn't properly put document to address {0}".format(endpoint))
                    eprint(r.text)
                else:
                    print("Document updated at: " + time.strftime("%D %H:%M:%S", time.localtime()))
                    break
        if tries > MAX_CONNECTION_TRIES:
            error_string = "Information posting for document {0} failed too many times, aborting".format(str(doc))
            eprint(error_string)
            raise ConnectionError(error_string)

    def experiment_exists(self, experiment_id):
        info = self.get_document(experiment_id, self.experiments_full_endpoint)
        if info:
            return True
        return False

    def send_experiment_docs(self, documents):
        for experiment in documents:
            eprint("Retrieving experiment {0}".format(experiment["experiment_id"]))
            info = self.get_document(experiment["experiment_id"], self.experiments_full_endpoint)
            self.post_doc(experiment, info, self.experiments_full_endpoint)

    def send_test_docs(self, documents):
        for test in documents:
            if not self.experiment_exists(test["experiment_id"]):
                # Experiment doesn't exist
                eprint("[SNITCH MONGODB AGENT] couldn't properly post documents to address {0}".format(
                    self.experiments_full_endpoint))
                eprint("[SNITCH MONGODB AGENT] experiment {0} doesn't exist".format(test["experiment_id"]))
                continue
            info = self.get_document(test["test_id"], self.tests_full_endpoint)
            self.post_doc(test, info, self.tests_full_endpoint)

    def send_docs(self, documents):
        if len(documents["experiment"]) >= 1:
            self.send_experiment_docs(documents["experiment"])
        if len(documents["test"]) >= 1:
            self.send_test_docs(documents["test"])

    @staticmethod
    def get_legth_docs(documents):
        num_docs = 0
        for key in documents:
            num_docs += len(documents[key])
        return num_docs

    def delete_test(self, experiment_id, test_id):
        if self.experiment_exists(experiment_id):
            test = self.get_test_by_name(experiment_id, test_id)
            if not test:
                print("Document doesn't {0} exist".format(test_id))
                return
            headers["If-Match"] = test["_etag"]
            tests_full_endpoint = "{0}/{1}".format(self.tests_full_endpoint, test["_id"])
            r = requests.delete(tests_full_endpoint, headers=headers)
            if r.status_code != 204:
                eprint("[MONGODB AGENT] couldn't properly delete document to address {0}".format(tests_full_endpoint))
                eprint(r.text)
            else:
                print("Document deleted at: " + time.strftime("%D %H:%M:%S", time.localtime()))
        else:
            return False

    def delete_experiment(self, experiment_id):
        if self.experiment_exists(experiment_id):
            experiment = self.get_document(experiment_id, self.experiments_full_endpoint)
            headers["If-Match"] = experiment["_etag"]
            experiment_full_endoint = "{0}/{1}".format(self.experiments_full_endpoint, experiment["_id"])
            r = requests.delete(experiment_full_endoint, headers=headers)
            if r.status_code != 204:
                eprint("[MONGODB AGENT] couldn't properly delete document in {0}".format(experiment_full_endoint))
                eprint(r.text)
            else:
                print("Document deleted at: " + time.strftime("%D %H:%M:%S", time.localtime()))
        else:
            return False

    def get_all_experiments(self):
        last_page = False
        all_experiments = list()
        host_endpoint = "http://{0}:{1}".format(mongodb_ip, mongodb_port)
        endpoint = "{0}/{1}".format(host_endpoint, tests_post_endpoint)
        while not last_page:
            data = self.get_paginated_experiments(endpoint)
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

    @staticmethod
    def get_paginated_experiments(endpoint):
        try:
            r = requests.get(endpoint)
            return r.json()
        except requests.ConnectionError as error:
            eprint("Error with request {0}".format(str(error)))
            return None

    def get_experiment_tests(self, experiment_id, mongodb_address, endpoint, tests=list()):
        try:
            r = requests.get(endpoint)
        except requests.ConnectionError as error:
            eprint("Error with request {0}".format(str(error)))
            return None

        response = r.json()
        tests = tests + response["_items"]
        max_results_per_page = response["_meta"]["max_results"]
        num_page = response["_meta"]["page"]
        total_docs = response["_meta"]["total"]

        if max_results_per_page * num_page < total_docs:
            # Still documents to retrieve in next page
            next_endpoint = 'http://{0}/{1}'.format(mongodb_address, response["_links"]["next"]["href"])
            return self.get_experiment_tests(experiment_id, mongodb_address, next_endpoint, tests=tests)
        else:
            return tests


if __name__ == '__main__':
    abort = False

    docs = dict()
    docs["experiment"] = []
    docs["test"] = []

    agent = MongoDBTimestampAgent()

    eprint("[MONGODB AGENT] Mongodb agent started, waiting for input to send.")
    eprint("[MONGODB AGENT] Endpoints to use will be {0} to experiments and {1} to tests".format(
        agent.get_experiments_endpoint(), agent.get_tests_endpoint()
    ))

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

            length_docs = agent.get_legth_docs(docs)
            if length_docs >= post_doc_buffer_length:
                agent.send_docs(docs)
                docs = dict()
                docs["experiment"] = []
                docs["test"] = []

                if abort:
                    exit(1)
                sys.stdout.flush()
        agent.send_docs(docs)
    except IOError as e:
        eprint("[MONGODB AGENT] terminated")
        eprint(e)
    except KeyboardInterrupt:
        eprint("[MONGODB AGENT] terminated")
        agent.send_docs(docs)
