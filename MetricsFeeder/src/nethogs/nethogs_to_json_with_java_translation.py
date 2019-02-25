#!/usr/bin/env python
from __future__ import print_function
import sys
import fileinput

import nethogs_to_csv
from src.pipelines import field_translator as field_translator
from src.pipelines import hadoop_java_translator as hadoop_java_translator
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
    eprint("[NETHOGS-with-java TO JSON] error in : " + str(error))
    sys.exit(1)


def process_line(line):
    metrics_dict, tags_dict, template = csv_to_json.initialize()

    if line == "":
        return
    line_in_csv = nethogs_to_csv.process_line(line)
    if line_in_csv:
        line_translated = field_translator.process_line(line_in_csv)
        line_java_translated = hadoop_java_translator.process_line(line_translated)
        for json in csv_to_json.process_line(line_java_translated, metrics_dict, tags_dict, template):
            TSDB_json = json_to_TSDB_json.process_line(json)
            print(TSDB_json)


def behave_like_pipeline():
    try:
        for line in fileinput.input():
            process_line(line)
    except KeyboardInterrupt:
        # Exit silently
        good_finish()
    except IOError as e:
        bad_finish(e)


def main():
    behave_like_pipeline()


if __name__ == "__main__":
    main()
