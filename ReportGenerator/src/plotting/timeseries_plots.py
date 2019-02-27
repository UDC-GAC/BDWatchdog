#!/usr/bin/env python
from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt

from ReportGenerator.src.reporting.config import bdwatchdog_handler, STATIC_LIMITS
from ReportGenerator.src.reporting.latex_output import latex_print
from ReportGenerator.src.plotting.plot_utils import translate_plot_name_to_ylabel, line_style, dashes_dict, line_marker, save_figure, \
    get_y_limit
from ReportGenerator.src.reporting.utils import translate_metric



def plot_structure(test, test_name, structure, plots, start_time, end_time, add_plots_to_report=True):
    structure_name, structure_type = structure
    benchmark_type = test["test_name"].split("_")[0]

    for plot in plots:
        max_ts_point_value = 10

        check_range, ymin, ymax = False, 0, None
        if plot == "disk":
            check_range, ymin, ymax = True, 0, 200
            if structure_type == "node":
                check_range, ymin, ymax = True, 0, 200
            elif structure_type == "app":
                check_range, ymin, ymax = True, 0, 1200

        width, height = 8, 3
        fig = plt.figure(figsize=(width, height))
        ax1 = fig.add_subplot(111)

        for metric in plots[plot]:
            metric_name = metric[0]

            # Get the time series data
            timeseries = test["resources"][structure_name][metric_name]
            if not timeseries:
                continue

            # Apply range trimming if necessary
            if check_range:
                timeseries = bdwatchdog_handler.perform_timeseries_range_apply(timeseries, ymin, ymax)

            # Convert the time stamps to times relative to 0 (basetime)
            basetime = int(list(timeseries.keys())[0])
            x = list(map(lambda point: int(point) - basetime, timeseries))

            # Get the time series points
            if plot == "cpu":
                y = list(timeseries.values())
            elif plot == "mem":
                # Tranlsate to GB
                y = list(map(lambda point: int(int(point) / 1024), timeseries.values()))
            else:
                y = list(timeseries.values())

            # Plot a time series
            linestyle = line_style[plot][metric_name]
            ax1.plot(x, y,
                     label=translate_metric(metric_name),
                     linestyle=linestyle,
                     dashes=dashes_dict[linestyle],
                     marker=line_marker[plot][metric_name],
                     markersize=6,
                     markevery=5)

            # Update the maximum time series point value
            max_ts_point_value = max(max_ts_point_value, max(y))

        # Set properties to the whole plot
        plt.xlabel('Time (s)')
        plt.ylabel(translate_plot_name_to_ylabel(plot), style="italic", weight="bold", )
        plt.title('')
        plt.grid(True)
        plt.legend(loc='upper right',
                   shadow=False,
                   fontsize='small',
                   fancybox=True,
                   facecolor='#afeeee')

        # Set y limits
        top, bottom = get_y_limit("plot_structure", max_ts_point_value, resource_label=plot,
                                  structure_type=structure_type, static_limits=STATIC_LIMITS)
        plt.ylim(top=top, bottom=0)

        # May be inaccurate up to +- 'downsample' seconds,
        # because the data may start a little after the specified 'start' time or end
        # a little before the specified 'end' time
        plt.xticks(np.arange(0, int(end_time) - int(start_time), step=100))

        # Save the plot
        figure_name = "{0}_{1}.{2}".format(structure_name, plot, "svg")
        figure_filepath_directory = "{0}/{1}/{2}".format("timeseries_plots", benchmark_type, test_name)
        save_figure(figure_filepath_directory, figure_name, fig)

        if add_plots_to_report:
            figure_name = "{0}_{1}_{2}.{3}".format(test_name, structure_name, plot, "eps")
            save_figure(".", figure_name, fig, format="eps")
            latex_print("![Resource for experiment {0} in structure {1}]({2})".format(
                test_name, structure_name, figure_name))
        plt.close()


def get_plots():
    plots = dict()
    plots["app"] = dict()

    plots["app"]["untreated"] = {"cpu": [], "mem": []}
    plots["app"]["serverless"] = {"cpu": [], "mem": []}

    # plots["app"]["untreated"] = {"cpu": [], "mem": [], "disk": [], "net": [], "energy": []}
    # plots["app"]["serverless"] = {"cpu": [], "mem": [], "disk": [], "net": [], "energy": []}
    # plots["app"]["energy"] = {"cpu": [], "mem": [], "disk": [], "net": [], "energy": []}

    plots["app"]["untreated"]["cpu"] = [('structure.cpu.current', 'structure'), ('structure.cpu.usage', 'structure')]
    plots["app"]["serverless"]["cpu"] = plots["app"]["untreated"]["cpu"]
    # plots["app"]["energy"]["cpu"] = plots["app"]["untreated"]["cpu"]

    plots["app"]["untreated"]["mem"] = [('structure.mem.current', 'structure'), ('structure.mem.usage', 'structure')]
    plots["app"]["serverless"]["mem"] = plots["app"]["untreated"]["mem"]
    # plots["app"]["energy"]["mem"] = plots["app"]["untreated"]["mem"]

    # plots["app"]["untreated"]["disk"] = [('structure.disk.current', 'structure'), ('structure.disk.usage', 'structure')]
    # plots["app"]["serverless"]["disk"] = plots["app"]["untreated"]["disk"]
    # plots["app"]["energy"]["disk"] = plots["app"]["untreated"]["disk"]

    # plots["app"]["untreated"]["net"] = [('structure.net.current', 'structure'), ('structure.net.usage', 'structure')]
    # plots["app"]["serverless"]["net"] = plots["app"]["untreated"]["net"]
    # plots["app"]["energy"]["net"] = plots["app"]["untreated"]["net"]
    #
    # plots["app"]["untreated"]["energy"] = [('structure.energy.max', 'structure'),
    #                                        ('structure.energy.usage', 'structure')]
    # plots["app"]["serverless"]["energy"] = plots["app"]["untreated"]["energy"]
    # plots["app"]["energy"]["energy"] = plots["app"]["untreated"]["energy"]

    plots["node"] = dict()
    # plots["node"]["untreated"] = {"cpu": [], "mem": [], "disk": [], "net": []}
    # plots["node"]["serverless"] = {"cpu": [], "mem": [], "disk": [], "net": []}

    plots["node"]["untreated"] = {"cpu": [], "mem": []}
    plots["node"]["serverless"] = {"cpu": [], "mem": []}
    # plots["node"]["energy"] = {"cpu": [], "mem": [], "disk": [], "net": []}

    plots["node"]["untreated"]["cpu"] = [('structure.cpu.current', 'structure'), ('structure.cpu.usage', 'structure')
                                         # ('proc.cpu.user', 'host'),('proc.cpu.kernel', 'host')
                                         ]
    plots["node"]["serverless"]["cpu"] = [('structure.cpu.current', 'structure'), ('structure.cpu.usage', 'structure'),
                                          # ('proc.cpu.user', 'host'),('proc.cpu.kernel', 'host'),
                                          ('limit.cpu.lower', 'structure'), ('limit.cpu.upper', 'structure')]
    # plots["node"]["energy"]["cpu"] = plots["node"]["untreated"]["cpu"]

    plots["node"]["untreated"]["mem"] = [('structure.mem.current', 'structure'), ('structure.mem.usage', 'structure')]
    # ('proc.mem.resident', 'host')]
    plots["node"]["serverless"]["mem"] = [('structure.mem.current', 'structure'), ('structure.mem.usage', 'structure'),
                                          # ('proc.mem.resident', 'host'),
                                          ('limit.mem.lower', 'structure'), ('limit.mem.upper', 'structure')]
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

    return plots
