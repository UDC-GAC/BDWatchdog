#!/usr/bin/env python
from __future__ import print_function
import sys
import fileinput
import time
import requests
import json
import ast

from FlamegraphsGenerator.src.utils import get_mongodb_POST_endpoint


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


max_failed_connection_tries = 4
post_doc_buffer_length = 10000


def send_docs(docs, post_endpoint):
    headers = {'content-type': 'application/json'}

    try:
        r = requests.post(post_endpoint, headers=headers, data=json.dumps(docs))
        if r.status_code != 201:
            eprint("[MONGODB SENDER] couldn't properly post documents to address " + post_endpoint)
            eprint(r.text)
            return False
        else:
            print("Post was done at: " + time.strftime("%D %H:%M:%S", time.localtime()) + " with " + str(
                len(docs)) + " documents , timestamp is " + str(time.time()))
            return True
    except requests.exceptions.ConnectionError as e:
        eprint("[MONGODB SENDER] couldn't properly post documents to address " + post_endpoint)
        eprint(e)
        return False


def main():
    post_endpoint = get_mongodb_POST_endpoint()
    failed_connections = 0
    json_documents = []
    try:
        for line in fileinput.input():
            try:
                new_doc = ast.literal_eval(line)
                json_documents = json_documents + [new_doc]
            except ValueError:
                print("Error with document " + str(line))
                continue

            length_docs = len(json_documents)
            if length_docs >= post_doc_buffer_length:
                if not send_docs(json_documents, post_endpoint):
                    failed_connections += 1
                json_documents = []

                if failed_connections >= max_failed_connection_tries:
                    eprint(
                        "[MONGODB SENDER] couldn't send documents to address " + post_endpoint + " and tried for " + str(
                            failed_connections) + " times, aborting")
                    exit(1)
                sys.stdout.flush()
        send_docs(json_documents, post_endpoint)
    except IOError as e:
        eprint("[MONGODB SENDER] terminated")
        eprint(e)
        pass
    except KeyboardInterrupt:
        eprint("[MONGODB SENDER] terminated")
        pass


if __name__ == "__main__":
    main()
