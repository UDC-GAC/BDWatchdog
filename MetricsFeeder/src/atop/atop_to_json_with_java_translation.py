#!/usr/bin/env python
from __future__ import print_function
import sys
import fileinput

import MetricsFeeder.src.atop.atop_to_csv as atop_to_csv
from MetricsFeeder.src.pipelines import field_filter as field_filter
from MetricsFeeder.src.pipelines import validator as validator
from MetricsFeeder.src.pipelines import custom_filter as custom_filter
from MetricsFeeder.src.pipelines import field_translator as field_translator
from MetricsFeeder.src.pipelines import value_filter as value_filter
from MetricsFeeder.src.pipelines import hadoop_java_translator as hadoop_java_translator
from MetricsFeeder.src.pipelines import csv_to_json as csv_to_json
from MetricsFeeder.src.pipelines import json_to_TSDB_json as json_to_TSDB_json


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def sigterm_handler(_signo, _stack_frame):
    good_finish()


def good_finish():
    sys.stdout.flush()
    sys.exit(0)


def bad_finish(error):
    eprint("[ATOP-with-java TO JSON] error in : " + str(error))
    sys.exit(1)


def process_line(line):
    metrics_dict, tags_dict, template = csv_to_json.initialize()

    if line == "SEP\n" or line.endswith("n\n") or line.endswith("n 0\n"):
        return
    line_in_csv = atop_to_csv.process_line(line)
    line_filtered = field_filter.process_line(line_in_csv)
    for result in line_filtered:
        line_validated = validator.process_line(result)
        if line_validated:
            line_refiltered = custom_filter.process_line(line_validated)
            if line_refiltered:
                line_translated = field_translator.process_line(line_refiltered)
                line_value_filtered = value_filter.process_line(line_translated)
                if line_value_filtered:
                    line_java_translated = hadoop_java_translator.process_line(line_value_filtered)
                    for json in csv_to_json.process_line(line_java_translated, metrics_dict, tags_dict, template):
                        TSDB_json = json_to_TSDB_json.process_line(json)
                        print(TSDB_json)


def previous_process(line):
    global process_function
    # Wait until you see the SEP line, marking the beginning of real time metrics
    if line == "SEP\n":
        process_function = process_line
        process_line(line)
        return
    else:
        pass


process_function = previous_process


def behave_like_pipeline():
    global process_function
    try:
        for line in fileinput.input():
            process_function(line)

    except KeyboardInterrupt:
        # Exit silently
        good_finish()
    except IOError as e:
        bad_finish(e)


def main():
    behave_like_pipeline()


if __name__ == "__main__":
    main()
