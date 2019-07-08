#!/usr/bin/env python
from __future__ import print_function
import pathlib

from ReportGenerator.src.reporting.config import ConfigContainer

OVERHEAD_VALUE_SIZE = 10
FIGURE_SIZE = (6, 4)

# Get the config
cfg = ConfigContainer()

line_marker = {"cpu": {
    "structure.cpu.current": "x",
    "structure.cpu.usage": "o",
    "limit.cpu.lower": "v",
    "limit.cpu.upper": "^",
    "proc.cpu.user": "*", "proc.cpu.kernel": "*"},
    "mem": {
        "structure.mem.current": "x",
        "structure.mem.usage": "o",
        "limit.mem.lower": "v",
        "limit.mem.upper": "^",
        "proc.mem.resident": "o"},
    "disk": {
        "structure.disk.current": "X",
        "structure.disk.usage": "*",
        "limit.disk.lower": "v",
        "limit.disk.upper": "^",
        "proc.disk.writes.mb": "*",
        "proc.disk.reads.mb": "*"},
    "net": {
        "structure.net.current": "X",
        "structure.net.usage": "*",
        "limit.net.lower": "v",
        "limit.net.upper": "^",
        "proc.net.tcp.in.mb": "*",
        "proc.net.tcp.out.mb": "*"},
    "energy": {
        "structure.energy.max": "X",
        "structure.energy.usage": "*"}
}

dashes_dict = {"-": (1, 0), "--": (5, 7)}
line_style = {"cpu": {
    "structure.cpu.current": "-",
    "structure.cpu.usage": "-",
    "limit.cpu.lower": "--",
    "limit.cpu.upper": "--",
    "proc.cpu.user": "-",
    "proc.cpu.kernel": "-"},
    "mem": {
        "structure.mem.current": "-",
        "structure.mem.usage": "-",
        "limit.mem.lower": "--",
        "limit.mem.upper": "--",
        "proc.mem.resident": "-"},
    "disk": {
        "structure.disk.current": "-",
        "structure.disk.usage": "-",
        "limit.disk.lower": "--",
        "limit.disk.upper": "--",
        "proc.disk.writes.mb": "-",
        "proc.disk.reads.mb": "-"},
    "net": {
        "structure.net.current": "-",
        "structure.net.usage": "-",
        "limit.net.lower": "--",
        "limit.net.upper": "--",
        "proc.net.tcp.in.mb": "-",
        "proc.net.tcp.out.mb": "-"},
    "energy": {
        "structure.energy.max": "-",
        "structure.energy.usage": "-"}
}


def translate_test_run_name_by_conf_number(conf_number, benchmark_type):
    map = {
        "terasort": {0: "baseline", 1: "cpu_mem", 2: "CPU_mem", 3: "cpu_MEM", 4: "CPU_MEM"},
        "pagerank": {0: "baseline", 1: "CPU_MEM"},
        "fixwindow": {0: "baseline", 1: "cpu_mem", 2: "CPU_mem", 3: "cpu_MEM", 4: "CPU_MEM"}
    }
    try:
        return map[benchmark_type][conf_number]
    except KeyError:
        return conf_number


def get_x_limit(plotting_method, max_x_limit, benchmark_type=None, static_limits=False):
    if static_limits:
        if plotting_method == "plot_structure":
            left, right = -30, 1000
            if benchmark_type == "terasort":
                left, right = (left, 800)
            elif benchmark_type == "pagerank":
                left, right = (left, 1200)
            elif benchmark_type == "fixwindow":
                left, right = (left, 1000)
            return left, right

    left, right = (-30, max_x_limit)
    return left, right


def get_y_limit(plotting_method, max_y_limit, benchmark_type=None, resource_label=None, structure_type=None,
                static_limits=False):
    if static_limits:
        if plotting_method == "resource_usage_with_stepping":
            top, bottom = 100, 100
            if resource_label == "cpu":
                if benchmark_type == "terasort":
                    top, bottom = (320, 0)
                elif benchmark_type == "pagerank":
                    top, bottom = (500, 0)
                elif benchmark_type == "fixwindow":
                    top, bottom = (350, 0)
            elif resource_label == "mem":
                if benchmark_type == "terasort":
                    top, bottom = (1600, 0)
                elif benchmark_type == "pagerank":
                    top, bottom = (2600, 0)
                elif benchmark_type == "fixwindow":
                    top, bottom = (2600, 0)
            return top, bottom
        elif plotting_method == "times_with_stepping":
            top, bottom = 100, 100
            if benchmark_type == "terasort":
                top, bottom = (15, 0)
            elif benchmark_type == "pagerank":
                top, bottom = (23, 0)
            elif benchmark_type == "fixwindow":
                top, bottom = (20, 0)
            return top, bottom
        elif plotting_method == "plot_structure":
            top, bottom = 100, 100
            if structure_type == "node":
                if resource_label == "cpu":
                    return 210, 0
                elif resource_label == "mem":
                    return 11, 0
            elif structure_type == "app":
                if resource_label == "cpu":
                    return 3000, 0
                elif resource_label == "mem":
                    return 130, 0
            else:
                return top, bottom

    limit = max_y_limit * cfg.Y_AMPLIFICATION_FACTOR
    top, bottom = (limit, 0)
    return top, bottom


def translate_plot_name_to_ylabel(plot_name):
    if plot_name == "cpu":
        return "CPU (shares)"
    elif plot_name == "mem":
        return "Memory (GiB)"
    else:
        return plot_name


def save_figure(figure_filepath_directory, figure_name, figure, format="svg"):
    figure_filepath = "{0}/{1}".format(figure_filepath_directory, figure_name)
    create_output_directory(figure_filepath_directory)
    figure.savefig(figure_filepath, bbox_inches="tight", format=format)


def create_output_directory(figure_filepath_directory):
    pathlib.Path(figure_filepath_directory).mkdir(parents=True, exist_ok=True)


def get_plots():
    plots = dict()
    plots["app"] = dict()
    plots["app"]["serverless"] = {"cpu": [], "mem": []}
    plots["node"]["serverless"] = {"cpu": [], "mem": []}
    return plots
