#!/usr/bin/env python
from __future__ import print_function

import sys
import time

from ReportGenerator.src.reporting.config import MONGODB_IP, MONGODB_PORT, EXPERIMENTS_POST_ENDPOINT
from ReportGenerator.src.reporting.experiments import report_experiment
from TimestampsSnitch.src.mongodb.mongodb_agent import get_document
from TimestampsSnitch.src.mongodb.mongodb_utils import get_all_experiments


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def report_all_experiments():
    host_endpoint = 'http://' + MONGODB_IP + ':' + MONGODB_PORT
    experiments = get_all_experiments(host_endpoint, EXPERIMENTS_POST_ENDPOINT)
    if experiments:
        for exp in experiments:
            time_start = time.time()
            report_experiment(exp)
            time_end = time.time()
            eprint("Reporting of experiment {0} took {1} seconds".format(exp["experiment_name"], time_end - time_start))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        report_all_experiments()
    else:
        experiment_name = sys.argv[1]
        experiments_full_endpoint = "http://{0}:{1}/{2}".format(MONGODB_IP, MONGODB_PORT, EXPERIMENTS_POST_ENDPOINT)
        experiment = get_document(experiment_name, experiments_full_endpoint)
        if experiment:
            report_experiment(experiment)
