#!/usr/bin/env python
from __future__ import print_function

import fileinput
import sys
import turbostat_to_csv as turbostat_to_csv

from src.pipelines import csv_to_json as csv_to_json
from src.pipelines import json_to_TSDB_json as json_to_TSDB_json


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def sigterm_handler(_signo, _stack_frame):
    good_finish()


def good_finish():
    sys.stdout.flush()
    sys.exit(0)


def bad_finish(error):
    eprint("[TURBOSTAT TO JSON] error in : " + str(error))
    sys.exit(1)


def process_line(line, metrics_dict, tags_dict, template):
    # line_in_csv = turbostat_to_csv.process_line(line)
    # if line_in_csv:
    #     for json in csv_to_json.process_line(line_in_csv, metrics_dict, tags_dict, template):
    #         TSDB_json = json_to_TSDB_json.process_line(json)
    #         print(TSDB_json)
    pass

def behave_like_pipeline():
    global process_function
    try:
        metrics_dict, tags_dict, template = csv_to_json.initialize()

        #while True:
        #    line = sys.stdin.readline()
        #    process_function(line, metrics_dict, tags_dict, template)

        for line in fileinput.input():
           process_function(line, metrics_dict, tags_dict, template)


        # for line in sys.stdin:
        #    process_function(line, metrics_dict, tags_dict, template)

    except KeyboardInterrupt:
        # Exit silently
        good_finish()
    except IOError as e:
        bad_finish(e)


def main():
    behave_like_pipeline()


if __name__ == "__main__":
    main()
