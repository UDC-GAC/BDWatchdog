# Copyright (c) 2019 Universidade da Coruna
# Authors:
#     - Jonatan Enes [main](jonatan.enes@udc.es, jonatan.enes.alvarez@gmail.com)
#     - Roberto R. Exposito
#     - Juan Tourino
#
# This file is part of the BDWatchdog framework, from
# now on referred to as BDWatchdog.
#
# BDWatchdog is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# BDWatchdog is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BDWatchdog. If not, see <http://www.gnu.org/licenses/>.


from __future__ import print_function

import sys
import select
import json
import traceback
import requests
import gzip
from io import BytesIO
import time
import os
from requests.exceptions import ReadTimeout
import yaml

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


# ENVIRONMENT VARIABLES #
POST_ENDPOINT_VARIABLE = "POST_ENDPOINT_PATH"
POST_DOC_BUFFER_LENGTH = "POST_DOC_BUFFER_LENGTH"
POST_DOC_BUFFER_TIMEOUT = "POST_DOC_BUFFER_TIMEOUT"
POST_SEND_DOCS_TIMEOUT = "POST_SEND_DOCS_TIMEOUT"
POST_SEND_DOCS_FAILED_TRIES = "POST_SEND_DOCS_FAILED_TRIES"

# Get services config variables
bdwatchdog_path = os.environ['BDWATCHDOG_PATH']
config_file = bdwatchdog_path + "/services_config.yml"
with open(config_file, "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

opentsdb_url = config['OPENTSDB_URL']
opentsdb_port = config['OPENTSDB_PORT']
post_endpoint_url = 'http://' + opentsdb_url + ":" + str(opentsdb_port) + "/api/put"

#post_endpoint = os.getenv(POST_ENDPOINT_VARIABLE, 'http://opentsdb:4242/api/put')
post_endpoint = os.getenv(POST_ENDPOINT_VARIABLE, post_endpoint_url)
post_doc_buffer_length = int(os.getenv(POST_DOC_BUFFER_LENGTH, 700))
post_doc_buffer_timeout = float(os.getenv(POST_DOC_BUFFER_TIMEOUT, 0.2))
post_send_docs_timeout = int(os.getenv(POST_SEND_DOCS_TIMEOUT, 3))
post_send_docs_failed_tries = int(os.getenv(POST_SEND_DOCS_FAILED_TRIES, 3))


def send_json_documents(json_documents, requests_session=None):
    headers = {"Content-Type": "application/json", "Content-Encoding": "gzip"}

    out = BytesIO()
    with gzip.GzipFile(fileobj=out, mode="wb") as f:
        f.write(json.dumps(json_documents).encode())

    try:
        if requests_session:
            r = requests_session.post(post_endpoint, headers=headers, data=out.getvalue(),
                                      timeout=post_send_docs_timeout)
        else:
            r = requests.post(post_endpoint, headers=headers, data=out.getvalue(),
                              timeout=post_send_docs_timeout)
        if r.status_code != 204 and r.status_code != 400:
            return False, {"error": r.json()}
        else:
            if r.status_code == 400:
                return True, {}
                # return False, {"error": r.json()}
            return True, {}
    except ReadTimeout:
        return False, {"error": "Server timeout"}
    except Exception as e:
        return False, {"error": str(e)}


def process_line(line):
    new_doc = None
    try:
        new_doc = json.loads(line)
    except ValueError as e:
        if not line:
            eprint("[TSDB SENDER] Empty line was received")
        else:
            eprint("[TSDB SENDER] Error with document " + str(line))
            eprint(e)
    return new_doc


def finish(json_documents, requests_session, message):
    success, info = send_json_documents(json_documents, requests_session)
    sys.stdout.flush()
    eprint("[TSDB SENDER] -> {0}".format(message))
    exit(1)

def flush_data_buffer(requests_session, json_documents, length, failed_connections):
    try:
        success, info = send_json_documents(json_documents, requests_session)
        if not success:
            eprint("[TSDB SENDER] couldn't properly post documents to address {0} error: {1}".format(
                post_endpoint, str(info)))
            failed_connections += 1
        else:
            print(f"Post was done at: {time.strftime('%D %H:%M:%S', time.localtime())} with {length} documents")
            failed_connections = 0  # Reset failed connections, at least this one was successfull now
            json_documents.clear()  # Empty document buffer
    except requests.exceptions.ConnectTimeout:
        failed_connections += 1
        eprint("[TSDB SENDER] couldn't send documents to address {0} and tried for {1} times".format(
            post_endpoint, failed_connections))

    if failed_connections >= post_send_docs_failed_tries:
        message = "terminated due to too much connection errors"
        finish(json_documents, requests_session, message)

    sys.stdout.flush()

    return failed_connections


def behave_like_pipeline():
    # PROGRAM VARIABLES #
    failed_connections = 0
    fails = 0
    MAX_FAILS = 10
    json_documents = []
    requests_session = requests.Session()
    try:
        while True:
            if select.select([sys.stdin,],[],[],post_doc_buffer_timeout)[0]:
                line = sys.stdin.readline()
                if line == "": # EOF
                    break

                new_doc = process_line(line)
                if not new_doc:
                    fails += 1
                    if fails >= MAX_FAILS:
                        message = "terminated due to too many read pipeline errors"
                        finish(json_documents, requests_session, message)
                    else:
                        continue
                else:
                    json_documents = json_documents + [new_doc]
                    fails = 0  # Reset fails
                length_docs = len(json_documents)
                if length_docs >= post_doc_buffer_length:
                    failed_connections = flush_data_buffer(requests_session, json_documents, length_docs, failed_connections)
            else:
                length_docs = len(json_documents)
                if length_docs > 0:
                    failed_connections = flush_data_buffer(requests_session, json_documents, length_docs, failed_connections)

    except KeyboardInterrupt:
        # Exit silently
        eprint("[TSDB SENDER] terminated with keyboard interrupt")
    except Exception as e:
        eprint("[TSDB SENDER] terminated with error: " + str(e))
        track = traceback.format_exc()
        eprint(track)

    message = "finishing"
    finish(json_documents, requests_session, message)

def main():
    behave_like_pipeline()


if __name__ == "__main__":
    main()
