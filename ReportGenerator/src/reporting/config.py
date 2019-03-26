#!/usr/bin/env python
from __future__ import print_function

import configparser
import os

from ReportGenerator.src.reporting.utils import get_int_value
from ReportGenerator.src.opentsdb import bdwatchdog

STATIC_LIMITS = True  # To be used to set specific values for the limits
Y_AMPLIFICATION_FACTOR = 1.3

def read_config(config_path, config_keys):
    config_dict = {}
    config = configparser.ConfigParser()
    config.read(os.path.join(_base_path, config_path))
    #TODO FIX check that the config file existsts, otherwise give a warning
    for key in config_keys:
        try:
            config_dict[key] = config['DEFAULT'][key]
        except KeyError:
            pass  # Key is not configured, leave it
    return config_dict


def create_environment(config_dict, config_keys, default_environment_values):
    custom_environment = os.environ.copy()
    for key in config_keys:
        if key in config_dict.keys():
            custom_environment[key] = config_dict[key]
        else:
            custom_environment[key] = default_environment_values[key]
    return custom_environment


_base_path = os.path.dirname(os.path.abspath(__file__))
config_path = "../../conf/report_generator_config.ini"
config_keys = [
    "MONGODB_IP",
    "MONGODB_PORT",
    "TESTS_DATABASE_NAME",
    "EXPERIMENTS_DATABASE_NAME",
    "MAX_CONNECTION_TRIES",
    "NUM_BASE_EXPERIMENTS",
    "MAX_DIFF_TIME",
    "PRINT_MISSING_INFO_REPORT",
    "PRINT_NODE_INFO",
    "GENERATE_APP_PLOTS",
    "GENERATE_NODES_PLOTS",
    "ADD_APP_PLOTS_TO_REPORT",
    "ADD_NODES_PLOTS_TO_REPORT",
    "TEST_TYPE_STEPPING",
    "PRINT_TEST_BASIC_INFORMATION",
    "NODES_LIST"

]
default_environment_values = {
    "MONGODB_IP": "mongodb",
    "MONGODB_PORT": 8000,
    "TESTS_DATABASE_NAME": "tests",
    "EXPERIMENTS_DATABASE_NAME": "experiments",
    "MAX_CONNECTION_TRIES": 3,
    "NUM_BASE_EXPERIMENTS": 3,
    "MAX_DIFF_TIME": 10,
    "PRINT_MISSING_INFO_REPORT": "true",
    "PRINT_NODE_INFO": "true",
    "GENERATE_APP_PLOTS": "true",
    "GENERATE_NODES_PLOTS": "true",
    "ADD_APP_PLOTS_TO_REPORT": "true",
    "ADD_NODES_PLOTS_TO_REPORT": "false",
    "TEST_TYPE_STEPPING": 3,
    "PRINT_TEST_BASIC_INFORMATION": "false",
    "NODES_LIST" : "node1,node2,node3,node4,node5,node6,node7,node8,node9"
}

ENV = create_environment(read_config(config_path, config_keys), config_keys, default_environment_values)

MAX_CONNECTION_TRIES = get_int_value(ENV, "MAX_CONNECTION_TRIES", default_environment_values["MAX_CONNECTION_TRIES"])
MAX_DIFF_TIME = get_int_value(ENV, "MAX_DIFF_TIME", default_environment_values["MAX_DIFF_TIME"])

ADD_APP_PLOTS_TO_REPORT = ENV["ADD_APP_PLOTS_TO_REPORT"] == "true"
ADD_NODES_PLOTS_TO_REPORT = ENV["ADD_NODES_PLOTS_TO_REPORT"] == "true"

BDWATCHDOG_APP_METRICS = [('structure.cpu.current', 'structure'),
                          ('structure.mem.current', 'structure'),
                          ('structure.disk.current', 'structure'),
                          ('structure.net.current', 'structure'),
                          ('structure.energy.max', 'structure'),
                          ('structure.cpu.usage', 'structure'),
                          ('structure.mem.usage', 'structure'),
                          ('structure.disk.usage', 'structure'),
                          ('structure.net.usage', 'structure'),
                          ('structure.energy.usage', 'structure')]

BDWATCHDOG_CONTAINER_METRICS = [('structure.cpu.current', 'structure'), ('proc.cpu.user', 'host'),
                                ('proc.cpu.kernel', 'host'), ('limit.cpu.upper', 'structure'),
                                ('limit.cpu.lower', 'structure'),
                                ('structure.mem.current', 'structure'), ('proc.mem.resident', 'host'),
                                ('proc.mem.virtual', 'host'), ('limit.mem.upper', 'structure'),
                                ('limit.mem.lower', 'structure'),
                                ('structure.disk.current', 'structure'), ('proc.disk.reads.mb', 'host'),
                                ('proc.disk.writes.mb', 'host'), ('limit.disk.upper', 'structure'),
                                ('limit.disk.lower', 'structure'),
                                ('structure.net.current', 'structure'), ('proc.net.tcp.out.mb', 'host'),
                                ('limit.net.upper', 'structure'), ('limit.net.lower', 'structure'),
                                ('proc.net.tcp.in.mb', 'host'), ('structure.energy.usage', 'structure')]

PRINTED_METRICS = ['structure.cpu.current', 'structure.cpu.usage', 'proc.cpu.user', 'proc.cpu.kernel',
                   'structure.mem.current', 'structure.mem.usage', 'proc.mem.resident', 'proc.mem.virtual',
                   'structure.disk.current', 'proc.disk.reads.mb', 'proc.disk.writes.mb', 'structure.net.current',
                   'proc.net.tcp.out.mb', 'proc.net.tcp.in.mb', 'structure.energy.usage']

MAX_COLUMNS = {"print_test_resources": 6, "print_summarized_tests_info": 8,
               "print_tests_resource_utilization_report": 8, "print_tests_resource_overhead_report": 8,
               "print_tests_by_resource_report": 6, "print_tests_resource_hysteresis_report": 8}

MONGODB_IP = ENV["MONGODB_IP"]
MONGODB_PORT = get_int_value(ENV, "MONGODB_PORT", default_environment_values["MONGODB_PORT"])
TESTS_POST_ENDPOINT = ENV["TESTS_DATABASE_NAME"]
EXPERIMENTS_POST_ENDPOINT = ENV["EXPERIMENTS_DATABASE_NAME"]

PRINT_MISSING_INFO_REPORT = ENV["PRINT_MISSING_INFO_REPORT"] == "true"
PRINT_NODE_INFO = ENV["PRINT_NODE_INFO"] == "true"
GENERATE_APP_PLOTS = ENV["GENERATE_APP_PLOTS"] == "true"
GENERATE_NODES_PLOTS = ENV["GENERATE_NODES_PLOTS"] == "true"
num_base_experiments = get_int_value(ENV, "NUM_BASE_EXPERIMENTS", default_environment_values["NUM_BASE_EXPERIMENTS"])

TEST_TYPE_STEPPING = get_int_value(ENV, "TEST_TYPE_STEPPING", default_environment_values["TEST_TYPE_STEPPING"])
bdwatchdog_handler = bdwatchdog.BDWatchdog()

USAGE_METRICS_SOURCE = [("structure.cpu.usage", ['proc.cpu.user', 'proc.cpu.kernel']),
                        ("structure.mem.usage", ['proc.mem.resident']),
                        ("structure.disk.usage", ['proc.disk.writes.mb', 'proc.disk.reads.mb']),
                        ("structure.net.usage", ['proc.net.tcp.in.mb', 'proc.net.tcp.out.mb']),
                        ("structure.energy.usage", ['structure.energy.usage'])
                        ]

PRINT_TEST_BASIC_INFORMATION = ENV["PRINT_TEST_BASIC_INFORMATION"] == "true"

NODES_LIST = ENV["NODES_LIST"]
NODES_LIST = NODES_LIST.rstrip('"').lstrip('"').split(",")
