#!/usr/bin/env python
from __future__ import print_function

import sys

from ReportGenerator.src.reporting.config import ReporterConfig
from ReportGenerator.src.reporting.latex_output import latex_print, print_latex_stress

from ReportGenerator.src.plotting.barplots import plot_tests_resource_usage, plot_tests_times, \
    plot_tests_times_with_stepping, plot_tests_resource_usage_with_stepping
from ReportGenerator.src.plotting.timeseries_plots import get_plots, plot_document

from ReportGenerator.src.reporting.utils import generate_duration, translate_metric, format_metric, flush_table, \
    print_basic_doc_info, some_test_has_missing_aggregate_information, get_test_type, generate_resources_timeseries


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class TestReporter():
    def __init__(self):
        # Get the config
        self.cfg = ReporterConfig()

    def process_test(self, test):
        test = generate_duration(test)
        test = generate_resources_timeseries(test, self.cfg)
        return test

    def generate_test_resource_plot(self, tests):
        for test in tests:
            if "end_time" not in test or "start_time" not in test:
                return

            start, end = test["start_time"], test["end_time"]
            plots = get_plots()

            if self.cfg.GENERATE_NODES_PLOTS:
                for node in self.cfg.NODES_LIST:
                    test_plots = plots["node"]["energy"]
                    structure = (node, "node")
                    plot_document(test, structure, test_plots, start, end)

            if self.cfg.GENERATE_APP_PLOTS:
                for app in self.cfg.APPS_LIST:
                    app_plots = plots["app"]["energy"]
                    structure = (app, "app")
                    plot_document(test, structure, app_plots, start, end)

    # PRINT TEST RESOURCE USAGES
    def print_test_resources(self, test, structures_list):
        if not test["resource_aggregates"] or test["resource_aggregates"] == "n/a":
            latex_print("RESOURCE INFO NOT AVAILABLE")
            return

        max_columns = self.cfg.MAX_COLUMNS["print_test_resources"]
        headers, rows, remaining_data, num_columns = ["structure", "aggregation"], dict(), False, 0
        for metric_name in self.cfg.PRINTED_METRICS:
            headers.append(translate_metric(metric_name))
            for structure_name in structures_list:

                # Initialize
                if structure_name not in rows:
                    rows[structure_name] = dict()

                for agg in ["SUM", "AVG"]:
                    if agg not in rows[structure_name]:
                        rows[structure_name][agg] = [structure_name, agg]

                    try:
                        rows[structure_name][agg].append(
                            format_metric(test["resource_aggregates"][structure_name][metric_name][agg], metric_name,
                                          agg))
                    except KeyError:
                        rows[structure_name][agg].append("n/a")

            num_columns += 1
            remaining_data = True
            if num_columns >= max_columns:
                self.flush_rows_with_aggregations(rows, headers)
                headers, rows, remaining_data, num_columns = ["structure", "aggregation"], dict(), False, 0

        if remaining_data:
            self.flush_rows_with_aggregations(rows, headers)

    def flush_rows_with_aggregations(self, rows, headers, table_caption=None):
        final_rows = list()
        for row in rows:
            final_rows += list(rows[row].values())
        flush_table(final_rows, headers, table_caption)

    # PRINT TEST RESOURCE OVERHEAD
    def print_tests_resource_overhead_report_with_stepping(self, tests, num_base_experiments=3):
        max_columns = self.cfg.MAX_COLUMNS["print_tests_resource_overhead_report_with_stepping"]
        resource_tuples = self.cfg.METRICS_FOR_OVERHEAD_REPORT

        overheads, base_values, headers, num_columns, remaining_data = dict(), dict(), ["resource"], 0, False

        if some_test_has_missing_aggregate_information(tests):
            return

        # Compute the overheads for the baseline tests
        for resource_tuple in resource_tuples:
            resource, usage_metric = resource_tuple
            # Initialize
            if resource not in overheads:
                overheads[resource] = [resource]
                base_values[resource] = 0
            for test in tests[:num_base_experiments]:
                base_values[resource] += test["resource_aggregates"]["ALL"][usage_metric]["SUM"]

            base_values[resource] = base_values[resource] / num_base_experiments
            overheads[resource].append("---")

        # Create the stepping header
        from_string = tests[0]["test_name"]
        to_string = tests[num_base_experiments - 1]["test_name"].split("_")[1]
        headers.append("{0} to {1}".format(from_string, to_string))

        num_columns += 1

        # Compute the overheads for the remaining tests using the step (number of same configuration tests)
        index = num_base_experiments
        step = self.cfg.TEST_TYPE_STEPPING
        while index < len(tests):
            for resource_tuple in resource_tuples:
                resource, usage_metric = resource_tuple
                summary = 0
                for test in tests[index:index + step]:
                    summary += test["resource_aggregates"]["ALL"][usage_metric]["SUM"]
                summary = summary / step
                overhead = summary / (base_values[resource])
                overheads[resource].append(str(int((overhead - 1) * 100)) + "%")

            # Create the stepping header
            from_string = tests[index]["test_name"]
            to_string = tests[index + step - 1]["test_name"].split("_")[1]
            headers.append("{0} to {1}".format(from_string, to_string))

            index += step

            num_columns += 1
            remaining_data = True
            if num_columns >= max_columns:
                flush_table(overheads.values(), headers)
                overheads, headers, num_columns, remaining_data = dict(), ["resource"], 0, False

        if remaining_data:
            flush_table(overheads.values(), headers)

    def print_tests_resource_overhead_report(self, tests, num_base_experiments=3, print_with_stepping=True):
        table_caption = "TESTs resource overhead"
        max_columns = self.cfg.MAX_COLUMNS["print_tests_resource_overhead_report"]
        resource_tuples = self.cfg.METRICS_FOR_OVERHEAD_REPORT

        overheads, base_values, headers, num_columns, remaining_data = dict(), dict(), ["resource"], 0, False

        for test in tests[:num_base_experiments]:
            headers.append(test["test_name"])
            for resource_tuple in resource_tuples:
                resource, usage_metric = resource_tuple
                if resource not in overheads:
                    overheads[resource] = [resource]
                    base_values[resource] = 0

                if test["resource_aggregates"] != "n/a":
                    overheads[resource].append("---")
                    base_values[resource] += test["resource_aggregates"]["ALL"][usage_metric]["SUM"]
                else:
                    overheads[resource].append("n/a")
        for resource in base_values:
            base_values[resource] = base_values[resource] / num_base_experiments

        num_columns += num_base_experiments

        for test in tests[num_base_experiments:]:
            headers.append(test["test_name"])
            for resource_tuple in resource_tuples:
                resource, usage_metric = resource_tuple

                if resource not in overheads:
                    overheads[resource] = [resource]

                if test["resource_aggregates"] != "n/a":
                    overhead = test["resource_aggregates"]["ALL"][usage_metric]["SUM"] / base_values[resource]
                    resource_overhead = str(int((overhead - 1) * 100)) + "%"
                else:
                    resource_overhead = "n/a"

                overheads[resource].append(resource_overhead)

            num_columns += 1
            remaining_data = True
            if num_columns >= max_columns:
                flush_table(overheads.values(), headers, table_caption)
                table_caption = None
                overheads, headers, num_columns, remaining_data = dict(), ["resource"], 0, False
        if remaining_data:
            flush_table(overheads.values(), headers, table_caption)

        plot_tests_resource_usage(tests)

        if print_with_stepping:
            self.print_tests_resource_overhead_report_with_stepping(tests, num_base_experiments)
            plot_tests_resource_usage_with_stepping(tests, num_base_experiments)

    # PRINT TEST RESOURCE UTILIZATION
    def print_tests_resource_utilization_with_stepping(self, tests):
        max_columns = self.cfg.MAX_COLUMNS["print_tests_resource_utilization_with_stepping"]
        headers, rows, num_columns, remaining_data = ["resource"], dict(), 0, False

        if some_test_has_missing_aggregate_information(tests):
            return

        # Set step to baseline number of tests or to the experimentation number of tests if the first is unavailable
        index = 0
        if self.cfg.NUM_BASE_EXPERIMENTS == 0:
            step = self.cfg.TEST_TYPE_STEPPING
        else:
            step = self.cfg.NUM_BASE_EXPERIMENTS

        # Process all the step subgroups
        while index < len(tests):
            for resource_tuple in self.cfg.RESOURCE_UTILIZATION_TUPLES:
                resource, current, usage = resource_tuple
                utilization_acum = 0
                # Initialize
                if resource not in rows:
                    rows[resource] = [resource]
                # For the inside step tests perform the aggregation
                for test in tests[index:index + step]:
                    available = test["resource_aggregates"]["ALL"][current]["SUM"]
                    used = test["resource_aggregates"]["ALL"][usage]["SUM"]
                    utilization = int(100 * used / available) - 1
                    utilization_acum += utilization

                rows[resource].append(str(int(utilization_acum / step)) + '%')

            # Create the stepping header
            from_string = tests[index]["test_name"]
            to_string = tests[index + step - 1]["test_name"].split("_")[1]
            headers.append("{0} to {1}".format(from_string, to_string))

            # Increase the index
            index += step

            # Set the step to the tests step
            step = self.cfg.TEST_TYPE_STEPPING

            num_columns += 1
            remaining_data = True
            if num_columns >= max_columns:
                flush_table(rows.values(), headers)
                headers, rows, num_columns, remaining_data = ["resource"], dict(), 0, False

        if remaining_data:
            flush_table(rows.values(), headers)

    def print_tests_resource_utilization(self, tests):
        max_columns = self.cfg.MAX_COLUMNS["print_tests_resource_utilization_report"]
        table_caption = "TESTs resource utilization"

        headers, rows, num_columns, remaining_data = ["resource"], dict(), 0, False

        for test in tests:
            headers.append(test["test_name"])

            for resource_tuple in self.cfg.RESOURCE_UTILIZATION_TUPLES:
                resource, current, usage = resource_tuple
                if resource not in rows:
                    rows[resource] = [resource]
                if test["resource_aggregates"] == "n/a":
                    rows[resource].append("n/a")
                else:
                    try:
                        available = test["resource_aggregates"]["ALL"][current]["SUM"]
                        used = test["resource_aggregates"]["ALL"][usage]["SUM"]
                        if available <= 0:
                            raise KeyError
                        else:
                            rows[resource].append(str(int(100 * used / available) - 1) + '%')
                    except KeyError:
                        eprint("Resource utilization for '{0}' skipped as no value for applied resource limits are "
                               "present and thus not utilization ratio can be computed".format(resource))
                        continue

            num_columns += 1
            remaining_data = True
            if num_columns >= max_columns:
                flush_table(rows.values(), headers, table_caption)
                table_caption = None
                headers, rows, num_columns, remaining_data = ["resource"], dict(), 0, False

        if remaining_data:
            flush_table(rows.values(), headers)

    # PRINT TEST RESOURCE MISSING DATA
    def report_resources_missing_data(self, tests):
        for test in tests:
            if "end_time" not in test or "start_time" not in test:
                return

            structures_list = self.cfg.NODES_LIST
            misses = dict()
            for metric in self.cfg.METRICS_TO_CHECK_FOR_MISSING_DATA:
                metric_name = metric[0]
                for structure in structures_list:
                    if metric_name in test["resources"][structure]:
                        timeseries = test["resources"][structure][metric_name]
                    else:
                        timeseries = None
                    if bool(timeseries):
                        structure_misses_list = self.cfg.bdwatchdog_handler.perform_check_for_missing_metric_info(
                            timeseries)
                        if not structure_misses_list:
                            continue
                    else:
                        # No timeseries were retrieved, so it is a 100% lost
                        structure_misses_list = [{"time": 0, "diff_time": test["duration"]}]

                    if metric_name not in misses:
                        misses[metric_name] = dict()
                    misses[metric_name][structure] = structure_misses_list

            if misses:
                print("\\textbf{TEST:}" + " {0}".format(test["test_name"]))

                aggregated_misses = dict()
                for metric in misses:
                    aggregated_misses[metric] = dict()
                    for structure in misses[metric]:
                        aggregated_misses[metric][structure] = sum(
                            miss['diff_time'] for miss in misses[metric][structure])

                for metric in aggregated_misses:
                    latex_print("For metric: {0}".format(metric))
                    total_missed_time = 0
                    for structure in aggregated_misses[metric]:
                        structure_missed_time = aggregated_misses[metric][structure]

                        latex_print(
                            "Silence of {0} seconds at node {1} accounting for a total of {2:.2f}\%".format(
                                structure_missed_time, structure,
                                float(100 * structure_missed_time / test["duration"])))
                        total_missed_time += structure_missed_time

                    print_latex_stress(
                        "Silence of {0} seconds at for ALL nodes accounting for a total of {1:.2f}\%".format(
                            total_missed_time,
                            float(100 * total_missed_time / (len(structures_list) * test["duration"]))))
                latex_print("&nbsp;")

    def print_tests_resource_usage(self, tests):
        table_caption = "TESTs total resource usages"
        max_columns = self.cfg.MAX_COLUMNS["print_tests_by_resource_report"]
        headers, rows, num_columns, remaining_data = ["resource", "aggregation"], dict(), 0, False
        for test in tests:
            headers.append(test["test_name"])
            metrics = list()
            for t in self.cfg.RESOURCE_UTILIZATION_TUPLES:
                metrics.append(t[1])
                metrics.append(t[2])
            for resource in metrics:
                if resource not in rows:
                    rows[resource] = dict()

                for agg in ["SUM", "AVG"]:
                    if agg not in rows[resource]:
                        rows[resource][agg] = [translate_metric(resource), agg]

                    if test["resource_aggregates"] == "n/a":
                        rows[resource][agg].append("n/a")
                    else:
                        try:
                            rows[resource][agg].append(
                                format_metric(test["resource_aggregates"]["ALL"][resource][agg], resource, agg))
                        except KeyError:
                            rows[resource][agg].append("n/a")

            num_columns += 1
            remaining_data = True
            if num_columns >= max_columns:
                self.flush_rows_with_aggregations(rows, headers, table_caption)
                table_caption = None
                headers, rows, num_columns, remaining_data = ["resource", "aggregation"], dict(), 0, False

        if remaining_data:
            self.flush_rows_with_aggregations(rows, headers, table_caption)

    def print_test_report(self, tests, print_node_info):
        # PRINT BASIC INFO ABOUT THE TEST
        for test in tests:
            print_basic_doc_info(test)

            # PRINT SPECIFIC RESOURCE INFO FOR EVERY NODE (OPTIONAL) AND FOR THE AGGREGATION
            if print_node_info:
                structures_list = list()
                for node in self.cfg.NODES_LIST:
                    structures_list.append(node)
                self.print_test_resources(test, structures_list)
                print("")

            structures_list = ["ALL", "aux_user0", "pre_user0", "comp_user0"]
            self.print_test_resources(test, structures_list)
            print("")

    # PRINT SUMMARIZED TESTS DURATIONS AND OVERHEADS
    def print_summarized_tests_info_with_stepping(self, tests, num_base_experiments, basetime):
        max_columns = 6
        headers, overheads, num_columns, remaining_data = [], ["overhead"], 0, False

        if some_test_has_missing_aggregate_information(tests):
            return

        # BASETIME
        headers.append(tests[0]["test_name"] + " to " + tests[num_base_experiments - 1]["test_name"].split("_")[1])
        overheads.append("---")

        num_columns += 1

        index = num_base_experiments
        while index < len(tests):
            duration = 0
            for test in tests[index:index + self.cfg.TEST_TYPE_STEPPING]:
                duration += test["duration"]
            # The average overhead
            overhead = duration / (self.cfg.TEST_TYPE_STEPPING * basetime)
            overhead = str(int((overhead - 1) * 100)) + "%"
            overheads.append(overhead)

            # Create the stepping header
            from_string = tests[index]["test_name"]
            to_string = tests[index + self.cfg.TEST_TYPE_STEPPING - 1]["test_name"].split("_")[1]
            headers.append("{0} to {1}".format(from_string, to_string))

            index += self.cfg.TEST_TYPE_STEPPING

            num_columns += 1
            remaining_data = True
            if num_columns >= max_columns:
                flush_table([overheads], headers)
                headers, overheads, num_columns, remaining_data = [], ["overhead"], 0, False

        if remaining_data:
            flush_table([overheads], headers)

    def print_tests_times(self, tests):
        max_columns = self.cfg.MAX_COLUMNS["print_summarized_tests_info"]
        table_caption = "TESTs durations and time benchmarking "

        headers, durations_seconds, durations_minutes, num_columns, remaining_data = \
            ["time"], ["seconds"], ["minutes"], 0, False

        for test in tests:
            headers.append(test["test_name"])
            seconds, minutes, overhead = "n/a", "n/a", "n/a"
            if test["duration"] != "n/a":
                seconds = test["duration"]
                minutes = "{:.2f}".format((test["duration"]) / 60)

            durations_seconds.append(seconds)
            durations_minutes.append(minutes)

            num_columns += 1
            remaining_data = True
            if num_columns >= max_columns:
                flush_table([durations_seconds, durations_minutes], headers, table_caption)
                table_caption = None
                headers, durations_seconds, durations_minutes, num_columns, remaining_data = \
                    ["time"], ["seconds"], ["minutes"], 0, False

        if remaining_data:
            flush_table([durations_seconds, durations_minutes], headers, table_caption)

    def print_summarized_tests_info(self, tests, num_base_experiments, print_with_stepping=True):
        max_columns = self.cfg.MAX_COLUMNS["print_summarized_tests_info"]
        table_caption = "TESTs durations and time benchmarking (over the first {0} experiments)".format(
            num_base_experiments)

        headers, overheads, durations_seconds, durations_minutes, num_columns, remaining_data = \
            ["time"], ["overhead"], ["seconds"], ["minutes"], 0, False
        basetime = 0

        if num_base_experiments == 0:
            basetime = 1
        else:
            for test in tests[:num_base_experiments]:
                headers.append(test["test_name"])
                basetime += test["duration"]
                overheads.append("---")
                durations_seconds.append(test["duration"])
                durations_minutes.append("{:.2f}".format((test["duration"]) / 60))

                num_columns += 1
                remaining_data = True
                if num_columns >= max_columns:
                    flush_table([durations_seconds, durations_minutes, overheads], headers, table_caption)
                    table_caption = None
                    headers, overheads, durations_seconds, durations_minutes, num_columns, remaining_data = \
                        ["time"], ["overhead"], ["seconds"], ["minutes"], 0, False

            basetime = basetime / num_base_experiments

        for test in tests[num_base_experiments:]:
            headers.append(test["test_name"])
            seconds, minutes, overhead = "n/a", "n/a", "n/a"
            if test["duration"] != "n/a":
                seconds = test["duration"]
                minutes = "{:.2f}".format((test["duration"]) / 60)
                overhead = test["duration"] / basetime
                overhead = str(int((overhead - 1) * 100)) + "%"

            durations_seconds.append(seconds)
            durations_minutes.append(minutes)
            overheads.append(overhead)

            num_columns += 1
            remaining_data = True
            if num_columns >= max_columns:
                flush_table([durations_seconds, durations_minutes, overheads], headers, table_caption)
                table_caption = None
                headers, overheads, durations_seconds, durations_minutes, num_columns, remaining_data = \
                    ["time"], ["overhead"], ["seconds"], ["minutes"], 0, False

        if remaining_data:
            flush_table([durations_seconds, durations_minutes, overheads], headers, table_caption)

        plot_tests_times(tests)

        if print_with_stepping:
            self.print_summarized_tests_info_with_stepping(tests, num_base_experiments, basetime)
            plot_tests_times_with_stepping(tests, num_base_experiments, basetime)
