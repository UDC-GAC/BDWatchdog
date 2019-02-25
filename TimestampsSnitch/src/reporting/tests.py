#!/usr/bin/env python
from __future__ import print_function

from TimestampsSnitch.src.reporting.config import BDWATCHDOG_CONTAINER_METRICS, MAX_COLUMNS, \
    GENERATE_NODES_PLOTS, ADD_APP_PLOTS_TO_REPORT, ADD_NODES_PLOTS_TO_REPORT, PRINTED_METRICS, \
    GENERATE_APP_PLOTS, BDWATCHDOG_APP_METRICS, TEST_TYPE_STEPPING, num_base_experiments, \
    USAGE_METRICS_SOURCE, NODES_LIST
from TimestampsSnitch.src.reporting.latex_output import latex_print, print_latex_stress

from TimestampsSnitch.src.reporting.plots.barplots import plot_tests_resource_usage, plot_tests_times, \
    plot_tests_times_with_stepping, plot_tests_resource_usage_with_stepping
from TimestampsSnitch.src.reporting.plots.timeseries_plots import get_plots, plot_structure, bdwatchdog_handler

from TimestampsSnitch.src.reporting.utils import generate_duration, translate_metric, format_metric, flush_table, \
    print_basic_doc_info, some_test_has_missing_aggregate_information, get_test_type


def process_test(test):
    test = generate_duration(test)
    test = generate_test_resources_timeseries(test)
    return test


def generate_test_resources_timeseries(test):
    #  Check that the needed start and end time are present, otherwise abort
    if "end_time" not in test or "start_time" not in test:
        test["resource_aggregates"] = "n/a"
        return test

    # Initialize variables
    test["resource_aggregates"], test["resources"] = dict(), dict()
    start, end = test["start_time"], test["end_time"]
    structures_list = NODES_LIST

    # Retrieve the timeseries from OpenTSDB and perform the per-structure aggregations
    # Slow loop due to network call
    for structure_name in structures_list:
        test["resources"][structure_name] = \
            bdwatchdog_handler.get_structure_timeseries(structure_name, start, end, BDWATCHDOG_CONTAINER_METRICS)

        test["resource_aggregates"][structure_name] = \
            bdwatchdog_handler.perform_structure_aggregations(start, end, test["resources"][structure_name])

    # Generate the per-structure time series 'usage' metrics (e.g., structure.cpu.usage)
    for structure_name in structures_list:
        for agg_metric in USAGE_METRICS_SOURCE:
            metric_name, metrics = agg_metric

            if metric_name not in test["resources"][structure_name]:
                test["resources"][structure_name][metric_name] = dict()

            first_metric = test["resources"][structure_name][metrics[0]]
            for time_point in first_metric:
                for metric in metrics:
                    if time_point not in test["resources"][structure_name][metric_name]:
                        test["resources"][structure_name][metric_name][time_point] = 0

                    test["resources"][structure_name][metric_name][time_point] += \
                        test["resources"][structure_name][metric][time_point]

    # Generate the per-structure aggregated 'usage' metrics (e.g., structure.cpu.usage)
    for structure_name in structures_list:
        for agg_metric in USAGE_METRICS_SOURCE:
            metric_name, metrics_to_aggregate = agg_metric

            if metric_name not in test["resource_aggregates"][structure_name]:
                test["resource_aggregates"][structure_name][metric_name] = dict()
                metric_aggregates = test["resource_aggregates"][structure_name][metric_name]
                metric_aggregates["SUM"] = 0
                metric_aggregates["AVG"] = 0

                metric_aggregates = test["resource_aggregates"][structure_name][metric_name]
                for metric in metrics_to_aggregate:
                    metric_aggregates["SUM"] += test["resource_aggregates"][structure_name][metric]["SUM"]

                summatory = metric_aggregates["SUM"]
                metric_aggregates["AVG"] = summatory / test["duration"]
            else:
                pass

    # Generate the aggregated ALL pseudo-metrics for the overall application (all the container nodes)
    test["resource_aggregates"]["ALL"] = dict()
    for structure_name in structures_list:
        for metric in test["resource_aggregates"][structure_name]:

            if metric not in test["resource_aggregates"]["ALL"]:
                test["resource_aggregates"]["ALL"][metric] = dict()

            metric_aggregates = test["resource_aggregates"]["ALL"][metric]
            structure_metric = test["resource_aggregates"][structure_name][metric]

            for aggregation in structure_metric:

                if aggregation not in metric_aggregates:
                    metric_aggregates[aggregation] = 0

                metric_aggregates[aggregation] += structure_metric[aggregation]

    # Retrieve and add the "app1" metrics
    test["resources"]["app1"] = \
        bdwatchdog_handler.get_structure_timeseries("app1", start, end, BDWATCHDOG_APP_METRICS)

    test["resource_aggregates"]["app1"] = \
        bdwatchdog_handler.perform_structure_aggregations(start, end, test["resources"]["app1"])

    # This metric is manually added because container structures do not have it, only application structures
    test["resource_aggregates"]["ALL"]["structure.energy.max"] = \
        test["resource_aggregates"]["app1"]["structure.energy.max"]

    return test


def generate_test_resource_plot(tests):
    for test in tests:
        if "end_time" not in test or "start_time" not in test:
            return

        start, end = test["start_time"], test["end_time"]
        apps = [("app1", "app")]
        nodes = list()
        for node in NODES_LIST:
            nodes.append((node, "node"))
        plots = get_plots()

        if GENERATE_APP_PLOTS:
            for structure in apps:
                test_plots = plots[structure[1]][get_test_type(test["test_name"], TEST_TYPE_STEPPING)]
                plot_structure(test, test["test_name"], structure, test_plots, start, end,
                               add_plots_to_report=ADD_APP_PLOTS_TO_REPORT)

        if GENERATE_NODES_PLOTS:
            for structure in nodes:
                test_plots = plots[structure[1]][get_test_type(test["test_name"], TEST_TYPE_STEPPING)]

                # Sequential
                plot_structure(test, test["test_name"], structure, test_plots, start, end,
                               add_plots_to_report=ADD_NODES_PLOTS_TO_REPORT)


# PRINT TEST RESOURCE USAGES
def print_test_resources(test, structures_list):
    if not test["resource_aggregates"] or test["resource_aggregates"] == "n/a":
        latex_print("RESOURCE INFO NOT AVAILABLE")
        return

    max_columns = MAX_COLUMNS["print_test_resources"]
    headers, rows, remaining_data, num_columns = ["structure", "aggregation"], dict(), False, 0
    for metric_name in PRINTED_METRICS:
        headers.append(translate_metric(metric_name))
        for structure in structures_list:
            structure_name = structure[2]
            if structure_name not in rows:
                rows[structure_name] = dict()

            for agg in ["SUM", "AVG"]:
                if agg not in rows[structure_name]:
                    rows[structure_name][agg] = [structure_name, agg]
                rows[structure_name][agg].append(
                    format_metric(test["resource_aggregates"][structure_name][metric_name][agg], metric_name, agg))

        num_columns += 1
        remaining_data = True
        if num_columns >= max_columns:
            flush_rows_with_aggregations(rows, headers)
            headers, rows, remaining_data, num_columns = ["structure", "aggregation"], dict(), False, 0

    if remaining_data:
        flush_rows_with_aggregations(rows, headers)


def flush_rows_with_aggregations(rows, headers, table_caption=None):
    final_rows = list()
    for row in rows:
        final_rows += list(rows[row].values())
    flush_table(final_rows, headers, table_caption)


def print_tests_resource_hysteresis_report(tests):
    max_columns = MAX_COLUMNS["print_tests_resource_hysteresis_report"]
    table_caption = "TESTs resource hysteresis"

    headers, rows, num_columns, remaining_data = list(), dict(), 0, False
    headers.append("resource")

    if some_test_has_missing_aggregate_information(tests):
        return

    for test in tests:
        headers.append(test["test_name"])

        for resource_tuple in [("cpu", "proc.cpu.user"), ("mem", "proc.mem.resident")]:
            resource, usage = resource_tuple

            if resource not in rows:
                rows[resource] = [resource]

            hysteresis = 0
            for structure in test["resources"]:
                if structure.startswith("node"):
                    structure_timeseries = test["resources"][structure][usage]
                    hysteresis += bdwatchdog_handler.perform_hysteresis_aggregation(structure_timeseries) / 1000

            rows[resource].append(hysteresis)

        num_columns += 1
        remaining_data = True
        if num_columns >= max_columns:
            flush_table(rows.values(), headers, table_caption)
            table_caption = None
            headers, rows, num_columns, remaining_data = list(), dict(), 0, False
            headers.append("resource")

    if remaining_data:
        flush_table(rows.values(), headers, table_caption)


# PRINT TEST RESOURCE OVERHEAD
def print_tests_resource_overhead_report_with_stepping(tests, num_base_experiments=3):
    max_columns = 6
    resource_tuples = [("cpu used", "structure.cpu.usage"), ("cpu allocated", "structure.cpu.current"),
                       ("mem used", "structure.mem.usage"), ("mem allocated", "structure.mem.current")
                       # ,("energy", "structure.energy.usage")
                       ]

    overheads, base_values, headers, num_columns, remaining_data = dict(), dict(), ["resource"], 0, False

    if some_test_has_missing_aggregate_information(tests):
        return

    # Compute the overheads for the baseline tests
    for resource_tuple in resource_tuples:
        resource, usage_metric = resource_tuple
        if resource not in overheads:
            overheads[resource] = [resource]
            base_values[resource] = 0
        for test in tests[:num_base_experiments]:
            base_values[resource] += test["resource_aggregates"]["ALL"][usage_metric]["SUM"]

        base_values[resource] = base_values[resource] / num_base_experiments
        overheads[resource].append("---")

    headers.append(tests[0]["test_name"] + " to " + tests[num_base_experiments - 1]["test_name"].split("_")[1])
    num_columns += 1

    # Compute the overheads for the remaining tests using the step (number of same configuration tests)
    index = num_base_experiments
    step = TEST_TYPE_STEPPING
    while index < len(tests):
        for resource_tuple in resource_tuples:
            resource, usage_metric = resource_tuple
            summary = 0
            for test in tests[index:index + step]:
                summary += test["resource_aggregates"]["ALL"][usage_metric]["SUM"]
            summary = summary / step
            overhead = summary / (base_values[resource])
            overheads[resource].append(str(int((overhead - 1) * 100)) + "%")

        headers.append(
            tests[index]["test_name"] + " to " + tests[index + step - 1]["test_name"].split("_")[1])

        index += step

        num_columns += 1
        remaining_data = True
        if num_columns >= max_columns:
            flush_table(overheads.values(), headers)
            overheads, headers, num_columns, remaining_data = dict(), ["resource"], 0, False

    if remaining_data:
        flush_table(overheads.values(), headers)


def print_tests_resource_overhead_report(tests, num_base_experiments=3, print_with_stepping=True):
    table_caption = "TESTs resource overhead"
    max_columns = MAX_COLUMNS["print_tests_resource_overhead_report"]
    resource_tuples = [("cpu used", "structure.cpu.usage"), ("cpu allocated", "structure.cpu.current"),
                       ("mem used", "structure.mem.usage"), ("mem allocated", "structure.mem.current"),
                       ("energy", "structure.energy.usage")
                       ]

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
        print_tests_resource_overhead_report_with_stepping(tests, num_base_experiments)
        plot_tests_resource_usage_with_stepping(tests, num_base_experiments)


# PRINT TEST RESOURCE UTILIZATION
def print_tests_resource_utilization_with_stepping(tests):
    max_columns = 6
    headers, rows, num_columns, remaining_data = ["resource"], dict(), 0, False

    if some_test_has_missing_aggregate_information(tests):
        return

    index = 0
    if num_base_experiments == 0:
        step = TEST_TYPE_STEPPING
    else:
        step = num_base_experiments

    while index < len(tests):
        for resource_tuple in [("cpu", "structure.cpu.current", "structure.cpu.usage"),
                               ("mem", "structure.mem.current", "structure.mem.usage")
                               #,("energy", "structure.energy.max", "structure.energy.usage")
                               ]:
            resource, current, usage = resource_tuple
            utilization_acum = 0
            if resource not in rows:
                rows[resource] = [resource]
            for test in tests[index:index + step]:
                available = test["resource_aggregates"]["ALL"][current]["SUM"]
                used = test["resource_aggregates"]["ALL"][usage]["SUM"]
                utilization = int(100 * used / available) - 1
                utilization_acum += utilization

            rows[resource].append(str(int(utilization_acum / step)) + '%')

        headers.append(
            tests[index]["test_name"] + " to " + tests[index + step - 1]["test_name"].split("_")[1])

        index += step
        step = TEST_TYPE_STEPPING

        num_columns += 1
        remaining_data = True
        if num_columns >= max_columns:
            flush_table(rows.values(), headers)
            headers, rows, num_columns, remaining_data = ["resource"], dict(), 0, False

    if remaining_data:
        flush_table(rows.values(), headers)


def print_tests_resource_utilization(tests, print_with_stepping=True):
    max_columns = MAX_COLUMNS["print_tests_resource_utilization_report"]
    table_caption = "TESTs resource utilization"

    headers, rows, num_columns, remaining_data = ["resource"], dict(), 0, False

    for test in tests:
        headers.append(test["test_name"])

        for resource_tuple in [("cpu", "structure.cpu.current", "structure.cpu.usage"),
                               ("mem", "structure.mem.current", "structure.mem.usage")]:
            resource, current, usage = resource_tuple
            if resource not in rows:
                rows[resource] = [resource]
            if test["resource_aggregates"] == "n/a":
                rows[resource].append("n/a")
            else:
                available = test["resource_aggregates"]["ALL"][current]["SUM"]
                used = test["resource_aggregates"]["ALL"][usage]["SUM"]
                rows[resource].append(str(int(100 * used / available) - 1) + '%')

        num_columns += 1
        remaining_data = True
        if num_columns >= max_columns:
            flush_table(rows.values(), headers, table_caption)
            table_caption = None
            headers, rows, num_columns, remaining_data = ["resource"], dict(), 0, False

    if remaining_data:
        flush_table(rows.values(), headers)

    if print_with_stepping:
        print_tests_resource_utilization_with_stepping(tests)


# PRINT TEST RESOURCE MISSING DATA
def report_resources_missing_data(tests):
    metrics_to_check = [('structure.cpu.current', 'structure'), ('proc.cpu.user', 'host'),
                        ('proc.cpu.kernel', 'host'),
                        ('structure.mem.current', 'structure'), ('proc.mem.resident', 'host'),
                        ('structure.energy.usage', 'structure')
                        #,('structure.energy.max', 'structure'),
                        ]
    # metrics_to_check += [('proc.mem.virtual', 'host'), ('proc.disk.writes.mb', 'host'),
    #                      ('structure.disk.current', 'structure'), ('proc.disk.reads.mb', 'host'),
    #                      ('structure.energy.usage', 'structure')]

    # metrics_to_check += [('proc.net.tcp.out.mb', 'host'),('structure.net.current', 'structure'), ('proc.net.tcp.in.mb', 'host')]

    for test in tests:
        if "end_time" not in test or "start_time" not in test:
            return

        structures_list = NODES_LIST
        misses = dict()
        for metric in metrics_to_check:
            metric_name = metric[0]
            for structure in structures_list:
                timeseries = test["resources"][structure][metric_name]
                if bool(timeseries):
                    structure_misses_list = bdwatchdog_handler.perform_check_for_missing_metric_info(timeseries)
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
                    aggregated_misses[metric][structure] = sum(miss['diff_time'] for miss in misses[metric][structure])

            for metric in aggregated_misses:
                latex_print("For metric: {0}".format(metric))
                total_missed_time = 0
                for structure in aggregated_misses[metric]:
                    structure_missed_time = aggregated_misses[metric][structure]

                    latex_print(
                        "Silence of {0} seconds at node {1} accounting for a total of {2:.2f}\%".format(
                            structure_missed_time, structure, float(100 * structure_missed_time / test["duration"])))
                    total_missed_time += structure_missed_time

                print_latex_stress(
                    "Silence of {0} seconds at for ALL nodes accounting for a total of {1:.2f}\%".format(
                        total_missed_time, float(100 * total_missed_time / (len(structures_list) * test["duration"]))))
            latex_print("&nbsp;")


def print_tests_resource_usage(tests):
    table_caption = "TESTs total resource usages"
    max_columns = MAX_COLUMNS["print_tests_by_resource_report"]
    headers, rows, num_columns, remaining_data = ["resource", "aggregation"], dict(), 0, False
    for test in tests:
        headers.append(test["test_name"])
        for resource in ["structure.cpu.current", "structure.cpu.usage", "structure.mem.current",
                         "structure.mem.usage", "structure.energy.usage"]:
            # , "structure.energy.usage"]:
            if resource not in rows:
                rows[resource] = dict()

            for agg in ["SUM", "AVG"]:
                if agg not in rows[resource]:
                    rows[resource][agg] = [translate_metric(resource), agg]

                if test["resource_aggregates"] == "n/a":
                    rows[resource][agg].append("n/a")
                else:
                    rows[resource][agg].append(
                        format_metric(test["resource_aggregates"]["ALL"][resource][agg], resource, agg))

        num_columns += 1
        remaining_data = True
        if num_columns >= max_columns:
            flush_rows_with_aggregations(rows, headers, table_caption)
            table_caption = None
            headers, rows, num_columns, remaining_data = ["resource", "aggregation"], dict(), 0, False

    if remaining_data:
        flush_rows_with_aggregations(rows, headers, table_caption)

    # plot_tests_resource_usage(tests)


def print_test_report(tests, print_node_info):
    # PRINT BASIC INFO ABOUT THE TEST
    for test in tests:
        print_basic_doc_info(test)

        # PRINT SPECIFIC RESOURCE INFO FOR EVERY NODE (OPTIONAL) AND FOR THE AGGREGATION
        if print_node_info:
            structures_list = list()
            for node in NODES_LIST:
                structures_list.append(("container", "host", node))

            # structures_list = [("container", "host", "node0"), ("container", "host", "node1"),
            #                    ("container", "host", "node2"), ("container", "host", "node3"),
            #                    ("container", "host", "node4"), ("container", "host", "node5")]
            print_test_resources(test, structures_list)
            print("")

        structures_list = [("container", "structure", "ALL")]
        print_test_resources(test, structures_list)
        print("")


# PRINT SUMMARIZED TESTS DURATIONS AND OVERHEADS
def print_summarized_tests_info_with_stepping(tests, num_base_experiments, basetime):
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
        for test in tests[index:index + TEST_TYPE_STEPPING]:
            duration += test["duration"]
        # The average overhead
        overhead = duration / (TEST_TYPE_STEPPING * basetime)
        overhead = str(int((overhead - 1) * 100)) + "%"
        overheads.append(overhead)

        headers.append(
            tests[index]["test_name"] + " to " + tests[index + TEST_TYPE_STEPPING - 1]["test_name"].split("_")[1])

        index += TEST_TYPE_STEPPING

        num_columns += 1
        remaining_data = True
        if num_columns >= max_columns:
            flush_table([overheads], headers)
            headers, overheads, num_columns, remaining_data = [], ["overhead"], 0, False

    if remaining_data:
        flush_table([overheads], headers)


def print_summarized_tests_info(tests, num_base_experiments, print_with_stepping=True):
    max_columns = MAX_COLUMNS["print_summarized_tests_info"]
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
    # num_columns += num_base_experiments

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
        print_summarized_tests_info_with_stepping(tests, num_base_experiments, basetime)
        plot_tests_times_with_stepping(tests, num_base_experiments, basetime)
