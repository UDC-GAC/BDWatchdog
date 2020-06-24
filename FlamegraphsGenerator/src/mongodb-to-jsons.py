#!/usr/bin/env python
from __future__ import print_function
import sys
import requests
import json

from FlamegraphsGenerator.src.utils import get_mongodb_GET_endpoint


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_data(start_time, end_time):
    get_endpoint = get_mongodb_GET_endpoint()
    payload = {'start_time': start_time, "end_time": end_time, "hostname": hostname}

    r = requests.get(get_endpoint, params=payload)
    if r.status_code != 200:
        eprint("COULDN'T GET DOCS")
        exit(1)
    else:
        print(json.dumps(r.json()))


if __name__ == "__main__":
    if len(sys.argv) < 4:
        eprint(
            "Missing arguments, at least two timestamps and a hostname are needed, first one will be start time and seconds one will be end time")
        exit(1)
    try:
        start_time = int(sys.argv[1])
        end_time = int(sys.argv[2])
        hostname = sys.argv[3]
        get_data(start_time, end_time)
    except ValueError:
        eprint("Parameters must be integers, in fact UNIX Timestamps, and a hostname or ALL for all hosts")
        exit(1)
