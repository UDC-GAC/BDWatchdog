#!/usr/bin/env python
from __future__ import print_function

import configparser
import os

from ReportGenerator.src.reporting.utils import get_int_value
from ReportGenerator.src.opentsdb import bdwatchdog


class ConfigContainer:
    __base_path = os.path.dirname(os.path.abspath(__file__))
    __config_path = "../../conf/report_generator_config.ini"
    __config_keys = [
        "TESTS_DATABASE_NAME",
        "EXPERIMENTS_DATABASE_NAME",
        "MAX_CONNECTION_TRIES",
        "MAX_DIFF_TIME",
        "PRINT_MISSING_INFO_REPORT",
        "PRINT_NODE_INFO",
        "GENERATE_APP_PLOTS",
        "GENERATE_NODES_PLOTS",
        "NODES_LIST",
        "APPS_LIST",
        "NUM_BASE_EXPERIMENTS",
        "TEST_TYPE_STEPPING",
        "PRINT_TEST_BASIC_INFORMATION",
        "STATIC_LIMITS"
    ]
    __default_environment_values = {
        "TESTS_DATABASE_NAME": "tests",
        "EXPERIMENTS_DATABASE_NAME": "experiments",
        "MAX_CONNECTION_TRIES": 3,
        "NUM_BASE_EXPERIMENTS": 3,
        "MAX_DIFF_TIME": 10,
        "PRINT_MISSING_INFO_REPORT": "true",
        "PRINT_NODE_INFO": "true",
        "GENERATE_APP_PLOTS": "true",
        "GENERATE_NODES_PLOTS": "true",
        "TEST_TYPE_STEPPING": 3,
        "PRINT_TEST_BASIC_INFORMATION": "false",
        "STATIC_LIMITS": "true",
        "NODES_LIST": "node1,node2,node3,node4,node5,node6,node7,node8,node9",
        "APPS_LIST" : "app1"
    }

    def read_config(self):
        config_dict = {}
        config = configparser.ConfigParser()
        config.read(os.path.join(self.__base_path, self.__config_path))
        # TODO FIX check that the config file exists, otherwise give a warning
        for key in self.__config_keys:
            try:
                config_dict[key] = config['DEFAULT'][key]
            except KeyError:
                pass  # Key is not configured, leave it
        return config_dict

    def create_environment(self):
        custom_environment = os.environ.copy()
        config_dict = self.read_config()
        for key in self.__config_keys:
            if key in config_dict.keys():
                custom_environment[key] = config_dict[key]
            else:
                custom_environment[key] = self.__default_environment_values[key]
        return custom_environment

    def __init__(self):
        self.Y_AMPLIFICATION_FACTOR = 1.3
        ENV = self.create_environment()

        self.MAX_CONNECTION_TRIES = get_int_value(ENV, "MAX_CONNECTION_TRIES",
                                                  self.__default_environment_values["MAX_CONNECTION_TRIES"])
        self.MAX_DIFF_TIME = get_int_value(ENV, "MAX_DIFF_TIME", self.__default_environment_values["MAX_DIFF_TIME"])

        self.BDWATCHDOG_APP_METRICS = [('structure.cpu.current', 'structure'),
                                       ('structure.mem.current', 'structure'),
                                       ('structure.disk.current', 'structure'),
                                       ('structure.net.current', 'structure'),
                                       ('structure.energy.max', 'structure'),
                                       ('structure.cpu.usage', 'structure'),
                                       ('structure.mem.usage', 'structure'),
                                       ('structure.disk.usage', 'structure'),
                                       ('structure.net.usage', 'structure'),
                                       ('structure.energy.usage', 'structure')]

        self.BDWATCHDOG_NODE_METRICS = [('structure.cpu.current', 'structure'), ('proc.cpu.user', 'host'),
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

        self.PRINTED_METRICS = ['structure.cpu.current', 'structure.cpu.usage', 'proc.cpu.user', 'proc.cpu.kernel',
                                'structure.mem.current', 'structure.mem.usage', 'proc.mem.resident', 'proc.mem.virtual',
                                'structure.disk.current', 'proc.disk.reads.mb', 'proc.disk.writes.mb',
                                'structure.net.current',
                                'proc.net.tcp.out.mb', 'proc.net.tcp.in.mb', 'structure.energy.usage']

        self.MAX_COLUMNS = {"print_test_resources": 6, "print_summarized_tests_info": 8,
                            "print_tests_resource_utilization_report": 8, "print_tests_resource_overhead_report": 8,
                            "print_tests_by_resource_report": 6, "print_tests_resource_hysteresis_report": 8,
                            "print_tests_resource_overhead_report_with_stepping":6,
                            "print_tests_resource_utilization_with_stepping":6}

        self.STATIC_LIMITS = ENV["STATIC_LIMITS"] == "true"

        self.PRINT_MISSING_INFO_REPORT = ENV["PRINT_MISSING_INFO_REPORT"] == "true"
        self.PRINT_NODE_INFO = ENV["PRINT_NODE_INFO"] == "true"
        self.GENERATE_APP_PLOTS = ENV["GENERATE_APP_PLOTS"] == "true"
        self.GENERATE_NODES_PLOTS = ENV["GENERATE_NODES_PLOTS"] == "true"
        self.NUM_BASE_EXPERIMENTS = get_int_value(ENV, "NUM_BASE_EXPERIMENTS",
                                                  self.__default_environment_values["NUM_BASE_EXPERIMENTS"])

        self.TEST_TYPE_STEPPING = get_int_value(ENV, "TEST_TYPE_STEPPING",
                                                self.__default_environment_values["TEST_TYPE_STEPPING"])
        self.bdwatchdog_handler = bdwatchdog.BDWatchdog()

        self.RESOURCE_UTILIZATION_TUPLES = [
            ("cpu", "structure.cpu.current", "structure.cpu.usage"),
            ("mem", "structure.mem.current", "structure.mem.usage")]
            # ,("energy", "structure.energy.max", "structure.energy.usage")

        self.USAGE_METRICS_SOURCE = [("structure.cpu.usage", ['proc.cpu.user', 'proc.cpu.kernel']),
                                     ("structure.mem.usage", ['proc.mem.resident']),
                                     ("structure.disk.usage", ['proc.disk.writes.mb', 'proc.disk.reads.mb']),
                                     ("structure.net.usage", ['proc.net.tcp.in.mb', 'proc.net.tcp.out.mb']),
                                     ("structure.energy.usage", ['structure.energy.usage'])
                                     ]

        self.METRICS_TO_CHECK_FOR_MISSING_DATA = [('structure.cpu.current', 'structure'), ('proc.cpu.user', 'host'),
                            ('proc.cpu.kernel', 'host'),
                            ('structure.mem.current', 'structure'), ('proc.mem.resident', 'host'),
                            ('structure.energy.usage', 'structure')
                            # ,('structure.energy.max', 'structure'),
                            ]

        self.PRINT_TEST_BASIC_INFORMATION = ENV["PRINT_TEST_BASIC_INFORMATION"] == "true"
        self.NODES_LIST = ENV["NODES_LIST"].rstrip('"').lstrip('"').split(",")

        self.APPS_LIST =  ENV["APPS_LIST"].rstrip('"').lstrip('"').split(",")
