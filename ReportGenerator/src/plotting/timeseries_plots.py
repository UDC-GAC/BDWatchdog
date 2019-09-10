#!/usr/bin/env python
from __future__ import print_function

import sys

import numpy as np
import matplotlib.pyplot as plt

from ReportGenerator.src.plotting.plot_utils import translate_plot_name_to_ylabel, line_style, dashes_dict, \
    line_marker, save_figure, get_y_limit, get_x_limit, TIMESERIES_FIGURE_SIZE
from ReportGenerator.src.reporting.config import ReporterConfig
from ReportGenerator.src.reporting.utils import translate_metric

# Get the config
cfg = ReporterConfig()


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def plot_document(doc, structure, plots, start_time, end_time):
    if "test_name" in doc:
        doc_name = doc["test_name"]
        benchmark_type = doc["test_name"].split("_")[0]
    else:
        doc_name = doc["experiment_id"]
        benchmark_type = "EXPERIMENT"

    structure_name, structure_type = structure

    for plot in plots:
        # Pre-Check for empty plot (no timeseries for all the metrics)
        empty_plot = True
        for metric in plots[plot]:
            metric_name = metric[0]
            if metric_name not in doc["resources"][structure_name] or doc["resources"][structure_name][metric_name]:
                empty_plot = False
        if empty_plot:
            eprint("Plot '{0}' for doc {1} has no data, skipping".format(plot, doc_name))
            continue

        fig = plt.figure(figsize=TIMESERIES_FIGURE_SIZE)
        ax1 = fig.add_subplot(111)

        #### Values used for trimming time series if necessary ####
        check_range, ymin, ymax = False, 0, None
        if plot == "disk":
            check_range, ymin, ymax = True, 0, 200
            if structure_type == "node":
                check_range, ymin, ymax = True, 0, 200
            elif structure_type == "app":
                check_range, ymin, ymax = True, 0, 1200
        ###################################################################

        #### Values used for setting the X and Y limits, without depending on actual time series values ####
        max_y_ts_point_value = cfg.YLIM
        max_x_ts_point_value = cfg.XLIM
        ###########################################################

        for metric in plots[plot]:
            metric_name = metric[0]
            structure_resources = doc["resources"][structure_name]

            # Get the time series data
            if metric_name not in structure_resources or not structure_resources[metric_name]:
                continue

            timeseries = structure_resources[metric_name]

            # Apply range trimming if necessary
            if check_range:
                timeseries = cfg.bdwatchdog_handler.perform_timeseries_range_apply(timeseries, ymin, ymax)

            # Convert the time stamps to times relative to 0 (basetime)
            basetime = int(list(timeseries.keys())[0])
            x = list(map(lambda point: int(point) - basetime, timeseries))

            # Get the time series points and rebase them if necessary
            if plot == "mem":
                # Tranlsate from MiB to GiB
                y = list(map(lambda point: int(int(point) / 1024), timeseries.values()))
            else:
                y = list(timeseries.values())

            # Set the maximum time series  time and value points
            max_y_ts_point_value = max(max_y_ts_point_value, max(y))
            max_x_ts_point_value = max(max_x_ts_point_value, max(x))

            # Plot a time series
            linestyle = line_style[plot][metric_name]
            ax1.plot(x, y,
                     label=translate_metric(metric_name),
                     linestyle=linestyle,
                     dashes=dashes_dict[linestyle],
                     marker=line_marker[plot][metric_name],
                     markersize=6,
                     markevery=5)

        # Set x and y limits
        top, bottom = get_y_limit("plot_structure", max_y_ts_point_value, resource_label=plot,
                                  structure_type=structure_type, static_limits=cfg.STATIC_LIMITS)

        left, right = get_x_limit("plot_structure", max_x_ts_point_value,
                                  benchmark_type=benchmark_type, static_limits=cfg.STATIC_LIMITS)

        plt.xlim(left=left, right=right)
        plt.ylim(top=top, bottom=0)

        # Set properties to the whole plot
        plt.xlabel('Time (s)')
        plt.ylabel(translate_plot_name_to_ylabel(plot), style="italic", weight="bold", )
        plt.title('')
        plt.grid(True, which="both")
        plt.legend(loc='upper right',
                   shadow=False,
                   fontsize='small',
                   fancybox=True,
                   facecolor='#afeeee')

        if cfg.STATIC_LIMITS:
            plt.xticks(np.arange(0, right, step=100))
        else:
            # May be inaccurate up to +- 'downsample' seconds,
            # because the data may start a little after the specified 'start' time or end
            # a little before the specified 'end' time
            plt.xticks(np.arange(0, int(end_time) - int(start_time), step=100))

        # Save the plot
        figure_name = "{0}_{1}.{2}".format(structure_name, plot, "svg")
        figure_filepath_directory = "{0}/{1}/{2}".format("timeseries_plots", benchmark_type, doc_name)
        save_figure(figure_filepath_directory, figure_name, fig)
        plt.close()


def get_plots():
    plots = dict()
    plots["app"] = dict()

    # plots["app"]["untreated"] = {"cpu": [], "mem": [], "disk": [], "net": [], "energy": []}
    plots["app"]["untreated"] = {"cpu": []}
    plots["app"]["serverless"] = {"cpu": []}
    plots["app"]["energy"] = {"cpu": [], "energy": []}

    plots["app"]["untreated"]["cpu"] = [('structure.cpu.current', 'structure'), ('structure.cpu.usage', 'structure')]
    plots["app"]["serverless"]["cpu"] = plots["app"]["untreated"]["cpu"]
    plots["app"]["energy"]["cpu"] = plots["app"]["untreated"]["cpu"]

    # plots["app"]["untreated"]["mem"] = [('structure.mem.current', 'structure'), ('structure.mem.usage', 'structure')]
    # plots["app"]["serverless"]["mem"] = plots["app"]["untreated"]["mem"]
    # plots["app"]["energy"]["mem"] = plots["app"]["untreated"]["mem"]

    # plots["app"]["untreated"]["disk"] = [('structure.disk.current', 'structure'), ('structure.disk.usage', 'structure')]
    # plots["app"]["serverless"]["disk"] = plots["app"]["untreated"]["disk"]
    # plots["app"]["energy"]["disk"] = plots["app"]["untreated"]["disk"]

    # plots["app"]["untreated"]["net"] = [('structure.net.current', 'structure'), ('structure.net.usage', 'structure')]
    # plots["app"]["serverless"]["net"] = plots["app"]["untreated"]["net"]
    # plots["app"]["energy"]["net"] = plots["app"]["untreated"]["net"]

    plots["app"]["untreated"]["energy"] = [('structure.energy.max', 'structure'),
                                           ('structure.energy.usage', 'structure')]
    plots["app"]["serverless"]["energy"] = plots["app"]["untreated"]["energy"]
    plots["app"]["energy"]["energy"] = plots["app"]["untreated"]["energy"]

    plots["node"] = dict()
    # plots["node"]["untreated"] = {"cpu": [], "mem": [], "disk": [], "net": [], "energy": []}
    plots["node"]["untreated"] = {"cpu": []}
    plots["node"]["serverless"] = {"cpu": []}
    plots["node"]["energy"] = {"cpu": [], "energy": []}

    plots["node"]["untreated"]["cpu"] = [('structure.cpu.current', 'structure'), ('structure.cpu.usage', 'structure')
                                         # ('proc.cpu.user', 'host'),('proc.cpu.kernel', 'host')
                                         ]
    plots["node"]["serverless"]["cpu"] = [('structure.cpu.current', 'structure'), ('structure.cpu.usage', 'structure'),
                                          # ('proc.cpu.user', 'host'),('proc.cpu.kernel', 'host'),
                                          ('limit.cpu.lower', 'structure'), ('limit.cpu.upper', 'structure')]
    plots["node"]["energy"]["cpu"] = plots["node"]["untreated"]["cpu"]

    # plots["node"]["untreated"]["mem"] = [('structure.mem.current', 'structure'), ('structure.mem.usage', 'structure')]
    # # ('proc.mem.resident', 'host')]
    # plots["node"]["serverless"]["mem"] = [('structure.mem.current', 'structure'), ('structure.mem.usage', 'structure'),
    #                                       # ('proc.mem.resident', 'host'),
    #                                       ('limit.mem.lower', 'structure'), ('limit.mem.upper', 'structure')]
    # plots["node"]["energy"]["mem"] = plots["node"]["untreated"]["mem"]

    # plots["node"]["untreated"]["disk"] = [('structure.disk.current', 'structure'), ('proc.disk.reads.mb', 'host'),
    #                                       ('proc.disk.writes.mb', 'host')]
    # plots["node"]["serverless"]["disk"] = plots["node"]["untreated"]["disk"]
    # plots["node"]["energy"]["disk"] = plots["node"]["untreated"]["disk"]
    #
    # plots["node"]["untreated"]["net"] = [('structure.net.current', 'structure'), ('proc.net.tcp.in.mb', 'host'),
    #                                      ('proc.net.tcp.out.mb', 'host')]
    # plots["node"]["serverless"]["net"] = plots["node"]["untreated"]["net"]
    # plots["node"]["energy"]["net"] = plots["node"]["untreated"]["net"]

    plots["node"]["energy"]["energy"] = [('structure.energy.usage', 'structure')]

    return plots
