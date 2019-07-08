#!/usr/bin/env python
from __future__ import print_function
import sys
import time

from ReportGenerator.src.reporting.config import ConfigContainer

from ReportGenerator.src.reporting.latex_output import print_latex_section
from ReportGenerator.src.reporting.tests import print_summarized_tests_info, process_test, print_tests_resource_usage, \
    print_tests_resource_utilization, print_tests_resource_overhead_report, print_test_report, \
    report_resources_missing_data, generate_test_resource_plot, print_tests_resource_hysteresis_report, \
    print_tests_times, print_tests_resource_utilization_with_stepping
from TimestampsSnitch.src.mongodb.mongodb_agent import MongoDBTimestampAgent
from ReportGenerator.src.reporting.utils import generate_duration, print_basic_doc_info, split_tests_by_test_type

# Get the config
cfg = ConfigContainer()

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
    agent = MongoDBTimestampAgent()
    tests = agent.get_experiment_tests(processed_experiment["experiment_id"])

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
        ("Tests durations", print_tests_times, [], True),
        ("Tests basic information", print_test_report, [cfg.PRINT_NODE_INFO], cfg.PRINT_TEST_BASIC_INFORMATION),
        ("Missing information report", report_resources_missing_data, [], cfg.PRINT_MISSING_INFO_REPORT),
        ("Resource utilization", print_tests_resource_utilization, [], True),

        ("Resource utilization with stepping", print_tests_resource_utilization_with_stepping, [], False),
        ("Tests durations and overheads", print_summarized_tests_info, [cfg.NUM_BASE_EXPERIMENTS], False),
        ("Resource overheads", print_tests_resource_overhead_report, [cfg.NUM_BASE_EXPERIMENTS],
         False and cfg.NUM_BASE_EXPERIMENTS != 0),
        ("Resource hysteresis", print_tests_resource_hysteresis_report, [], False)]

    for test_type in benchmarks:
        for report in test_reports:
            report_name, report_function, report_function_extra, bool_apply = report
            if bool_apply:
                eprint("Doing {0} for {1} at {2}".format(
                    report_name, test_type, time.strftime("%D %H:%M:%S", time.localtime())))
                print_latex_section("{0} for {1}".format(report_name, test_type))
                args = tuple([benchmarks[test_type]] + report_function_extra)
                report_function(*args)

    if cfg.GENERATE_APP_PLOTS or cfg.GENERATE_NODES_PLOTS:
        for test_type in benchmarks:
            eprint("Plotting resource plots for {0} at {1}".format(
                test_type, time.strftime("%D %H:%M:%S", time.localtime())))
            generate_test_resource_plot(benchmarks[test_type])
