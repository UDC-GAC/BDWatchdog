#!/usr/bin/env python
from __future__ import print_function
import sys
import time

from ReportGenerator.src.reporting.config import ReporterConfig, MongoDBConfig

from ReportGenerator.src.reporting.latex_output import print_latex_section
from ReportGenerator.src.reporting.TestReporter import TestReporter
from TimestampsSnitch.src.mongodb.mongodb_agent import MongoDBTimestampAgent
from ReportGenerator.src.reporting.utils import generate_duration, print_basic_doc_info, split_tests_by_test_type


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class ExperimentReporter():
    def __init__(self):
        self.cfg = ReporterConfig()
        mongoDBConfig = MongoDBConfig()
        self.timestampingAgent = MongoDBTimestampAgent(mongoDBConfig.get_config_as_dict())

    def process_experiment(self, exp):
        exp = generate_duration(exp)
        return exp

    def print_experiment_report(self, exp):
        # PRINT EXPERIMENT INFO
        print_latex_section("Experiment basic information")
        print_basic_doc_info(exp)

    def report_tests_serverless(self, processed_tests):
        testRepo = TestReporter()

        # PRINT TESTS RESOURCE INFO
        # (durations with overheads, resource usages, utilization, overheads, hysteresis and basic each test info)
        benchmarks = split_tests_by_test_type(processed_tests)
        test_reports = [
            ("Resource usages", testRepo.print_tests_resource_usage, [], True),
            ("Tests durations", testRepo.print_tests_times, [], True),
            ("Tests basic information", testRepo.print_test_report, [self.cfg.PRINT_NODE_INFO],
             self.cfg.PRINT_TEST_BASIC_INFORMATION),
            ("Missing information report", testRepo.report_resources_missing_data, [],
             self.cfg.PRINT_MISSING_INFO_REPORT),
            ("Resource utilization", testRepo.print_tests_resource_utilization, [], True),

            ("Resource utilization with stepping", testRepo.print_tests_resource_utilization_with_stepping, [], False),
            ("Tests durations and overheads", testRepo.print_summarized_tests_info, [self.cfg.NUM_BASE_EXPERIMENTS],
             False),
            ("Resource overheads", testRepo.print_tests_resource_overhead_report, [self.cfg.NUM_BASE_EXPERIMENTS],
             False and self.cfg.NUM_BASE_EXPERIMENTS != 0),
            ("Resource hysteresis", testRepo.print_tests_resource_hysteresis_report, [], False)]

        for test_type in benchmarks:
            for report in test_reports:
                report_name, report_function, report_function_extra, bool_apply = report
                if bool_apply:
                    eprint("Doing {0} for {1} at {2}".format(
                        report_name, test_type, time.strftime("%D %H:%M:%S", time.localtime())))
                    print_latex_section("{0} for {1}".format(report_name, test_type))
                    args = tuple([benchmarks[test_type]] + report_function_extra)
                    report_function(*args)

        if self.cfg.GENERATE_APP_PLOTS or self.cfg.GENERATE_NODES_PLOTS:
            for test_type in benchmarks:
                eprint("Plotting resource plots for {0} at {1}".format(
                    test_type, time.strftime("%D %H:%M:%S", time.localtime())))
                testRepo.generate_test_resource_plot(benchmarks[test_type])

    def report_tests_energy(self, processed_tests):
        testRepo = TestReporter()
        # PRINT TESTS RESOURCE INFO
        # (durations with overheads, resource usages, utilization, overheads, hysteresis and basic each test info)
        test_reports = [
            ("Resource usages", testRepo.print_tests_resource_usage, [], True),
            ("Tests durations", testRepo.print_tests_times, [], True),
            ("Tests basic information", testRepo.print_test_report, [self.cfg.PRINT_NODE_INFO],
             self.cfg.PRINT_TEST_BASIC_INFORMATION),
            ("Missing information report", testRepo.report_resources_missing_data, [],
             self.cfg.PRINT_MISSING_INFO_REPORT),
            ("Resource utilization", testRepo.print_tests_resource_utilization, [], True)]

        for report in test_reports:
            report_name, report_function, report_function_extra, bool_apply = report
            if bool_apply:
                eprint("Doing {0} at {1}".format(
                    report_name, time.strftime("%D %H:%M:%S", time.localtime())))
                print_latex_section("{0}".format(report_name))
                args = tuple([processed_tests] + report_function_extra)
                report_function(*args)

        if self.cfg.GENERATE_APP_PLOTS or self.cfg.GENERATE_NODES_PLOTS:
            testRepo.generate_test_resource_plot(processed_tests)

    def report_experiment(self, exp):
        testRepo = TestReporter()

        # GENERATE ALL ADDED INFO ABOUT EXPERIMENT
        processed_experiment = self.process_experiment(exp)

        # GENERATE ALL ADDED INFO ABOUT TESTS
        tests = self.timestampingAgent.get_experiment_tests(processed_experiment["experiment_id"])

        processed_tests = list()
        for test in tests:
            processed_tests.append(testRepo.process_test(test))

        # PRINT BASIC EXPERIMENT INFO
        eprint("Generating experiment info at {0}".format(time.strftime("%D %H:%M:%S", time.localtime())))
        self.print_experiment_report(processed_experiment)

        report_type = "serverless"
        report_type = "energy"

        if report_type == "serverless":
            self.report_tests_serverless(processed_tests)
        elif report_type == "energy":
            self.report_tests_energy(processed_tests)
        else:
            pass
