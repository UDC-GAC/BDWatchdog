#!/usr/bin/env python
from __future__ import print_function

import sys
import time
from tabulate import tabulate

from ReportGenerator.src.reporting.latex_output import latex_print


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_int_value(d, key, default):
    try:
        return int(d[key])
    except KeyError:
        eprint("Invalid configuration for {0}, using default value '{1}'".format(key, default))
        return default


def generate_duration(document):
    document["duration"] = "n/a"
    if "end_time" in document and "start_time" in document:
        document["duration"] = document["end_time"] - document["start_time"]
    return document


# PRINT EXPERIMENT OR TEST DOCUMENT INFORMATION
def print_basic_doc_info(doc):
    start_time_string, end_time_string, duration, duration_minutes = get_times_from_doc(doc)
    if "test_name" in doc:
        latex_print("\\textbf{TEST:}" + " {0}".format(doc["test_name"]))
    else:
        latex_print("\\textbf{EXPERIMENT:}" + " {0}".format(doc["experiment_id"]))
        latex_print("\\textbf{USER:}" + "{0}".format(doc["username"]))

    latex_print("\\textbf{START TIME:}" + " {0}".format(start_time_string))
    latex_print("\\textbf{END TIME:}" + " {0}".format(end_time_string))
    latex_print("\\textbf{DURATION:}" + " {0} seconds (about {1} minutes)".format(duration, duration_minutes) + "  ")


def flush_table(table, header, table_caption=None):
    # print_latex_vertical_space()
    print(tabulate(table, header))
    print("")
    if table_caption:
        latex_print("Table: " + table_caption)


def format_metric(value, label, aggregation):
    if aggregation == "AVG":
        number_format = "{:.2f}"
    else:
        number_format = "{:.0f}"

    if label.startswith("structure.cpu") or label.startswith("proc.cpu"):
        formatted_metric = "{0} vcore-s".format(number_format.format(value / 100))
    elif label.startswith("structure.mem") or label.startswith("proc.mem"):
        formatted_metric = "{0} GB-s".format(number_format.format(value / 1024))
    elif label.startswith("structure.disk") or label.startswith("proc.disk"):
        formatted_metric = "{0} GB".format(number_format.format(value / 1024))
    elif label.startswith("structure.net") or label.startswith("proc.net"):
        formatted_metric = "{0} Gbit".format(number_format.format(value / 1024))
    elif label.startswith("structure.energy"):
        if value >= 10000:
            value = value / 1000
        formatted_metric = "{0} KJoule".format(number_format.format(value))
    else:
        formatted_metric = value

    if aggregation == "AVG":
        formatted_metric += "/s"
    return formatted_metric


def some_test_has_missing_aggregate_information(tests):
    for test in tests:
        if test["resource_aggregates"] == "n/a":
            return True
    return False


def get_test_type(test_name, step):
    return "serverless"


def translate_benchmark(benchmark):
    if benchmark == "pagerank":
        return "PageRank"
    elif benchmark == "terasort":
        return "TeraSort"
    elif benchmark == "fixwindow":
        return "FixWindow"
    else:
        return benchmark


def translate_metric(metric):
    translated_metric = list()
    metric_fields = metric.split(".")

    metric_type = metric_fields[0]
    resource = metric_fields[1]
    measure_kind = metric_fields[2]

    if metric_type == "structure":
        if measure_kind == "usage":
            translated_metric.append("used")
        elif measure_kind == "current":
            translated_metric.append("allocated")
        elif measure_kind == "max":
            translated_metric.append("reserved")
        else:
            translated_metric.append(measure_kind)

    elif metric_type == "limit":
        if measure_kind == "upper":
            translated_metric.append("upper")
        elif measure_kind == "lower":
            translated_metric.append("lower")
        else:
            translated_metric.append(measure_kind)
        translated_metric.append("limit")

    elif metric_type == "proc":
        translated_metric.append(" ".join(metric_fields[2:]))

    return " ".join(translated_metric).capitalize()


def get_times_from_doc(doc):
    start_time_string, end_time_string, duration, duration_minutes = "n/a", "n/a", "n/a", "n/a"

    if "start_time" in doc:
        start_time_string = time.strftime("%D %H:%M:%S", time.localtime(doc["start_time"]))

    if "end_time" in doc:
        end_time_string = time.strftime("%D %H:%M:%S", time.localtime(doc["end_time"]))

    if "end_time" in doc and "start_time" in doc:
        duration = doc["duration"]
        duration_minutes = "{:.2f}".format(duration / 60)

    return start_time_string, end_time_string, duration, duration_minutes


def split_tests_by_test_type(tests):
    benchmarks = dict()
    for test in tests:
        test_benchmark = test["test_name"].split("_")[0]
        if test_benchmark not in benchmarks:
            benchmarks[test_benchmark] = list()
        benchmarks[test_benchmark].append(test)
    return benchmarks
