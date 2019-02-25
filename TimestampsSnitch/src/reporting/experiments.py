#!/usr/bin/env python
from __future__ import print_function
import sys
import time

from TimestampsSnitch.src.reporting.config import MONGODB_PORT, TESTS_POST_ENDPOINT, \
    MONGODB_IP, num_base_experiments, GENERATE_NODES_PLOTS, GENERATE_APP_PLOTS, PRINT_NODE_INFO, \
    PRINT_TEST_BASIC_INFORMATION, PRINT_MISSING_INFO_REPORT
from TimestampsSnitch.src.reporting.latex_output import print_latex_section
from TimestampsSnitch.src.reporting.tests import print_summarized_tests_info, process_test, print_tests_resource_usage, \
    print_tests_resource_utilization, print_tests_resource_overhead_report, print_test_report, \
    report_resources_missing_data, generate_test_resource_plot, print_tests_resource_hysteresis_report
from TimestampsSnitch.src.mongodb.mongodb_utils import get_experiment_tests
from TimestampsSnitch.src.reporting.utils import generate_duration, print_basic_doc_info, split_tests_by_test_type


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def process_experiment(exp):
    exp = generate_duration(exp)
    return exp


def print_experiment_report(exp):
    # PRINT EXPERIMENT INFO
    print_latex_section("Experiment basic information")
    print_basic_doc_info(exp)


def report_experiment(exp):
    # GENERATE ALL ADDED INFO ABOUT EXPERIMENT
    processed_experiment = process_experiment(exp)

    # GENERATE ALL ADDED INFO ABOUT TESTS
    mongodb_address = "{0}:{1}".format(MONGODB_IP, MONGODB_PORT)
    endpoint = "http://{0}/{1}".format(mongodb_address, TESTS_POST_ENDPOINT) + '/?where={"experiment_id":"' + \
               processed_experiment["experiment_id"] + '"}'
    tests = get_experiment_tests(processed_experiment["experiment_id"], mongodb_address, endpoint)

    processed_tests = list()
    for test in tests:
        processed_tests.append(process_test(test))

    # PRINT BASIC EXPERIMENT INFO
    eprint("Generating experiment info at {0}".format(time.strftime("%D %H:%M:%S", time.localtime())))
    print_experiment_report(processed_experiment)

    # PRINT TESTS RESOURCE INFO
    # (durations with overheads, resource usages, utilization, overheads, hysteresis and basic each test info)
    benchmarks = split_tests_by_test_type(processed_tests)
    test_reports = [
        ("Resource usages", print_tests_resource_usage, [], True),
        ("Tests durations and overheads", print_summarized_tests_info, [num_base_experiments], True),
        ("Resource utilization", print_tests_resource_utilization, [], True),
        ("Resource overheads", print_tests_resource_overhead_report, [num_base_experiments], num_base_experiments != 0),
        ("Resource hysteresis", print_tests_resource_hysteresis_report, [], False),
        ("Tests basic information", print_test_report, [PRINT_NODE_INFO], PRINT_TEST_BASIC_INFORMATION),
        ("Missing information report", report_resources_missing_data, [], PRINT_MISSING_INFO_REPORT)]

    for test_type in benchmarks:
        for report in test_reports:
            report_name, report_function, report_function_extra, generate = report
            if generate:
                eprint("Doing {0} for {1} at {2}".format(
                    report_name, test_type, time.strftime("%D %H:%M:%S", time.localtime())))
                print_latex_section("{0} for {1}".format(report_name, test_type))
                args = tuple([benchmarks[test_type]] + report_function_extra)
                report_function(*args)

    if GENERATE_APP_PLOTS or GENERATE_NODES_PLOTS:
        for test_type in benchmarks:
            eprint("Plotting resource plots for {0} at {1}".format(
                test_type, time.strftime("%D %H:%M:%S", time.localtime())))
            print_latex_section("Resource plots for {0}".format(test_type))
            generate_test_resource_plot(benchmarks[test_type])
