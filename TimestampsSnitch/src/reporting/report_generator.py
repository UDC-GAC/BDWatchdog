#!/usr/bin/env python
from __future__ import print_function

import sys
import time

from TimestampsSnitch.src.reporting.config import experiments_full_endpoint
from TimestampsSnitch.src.mongodb.mongodb_agent import get_document
from TimestampsSnitch.src.mongodb.mongodb_utils import get_all_experiments
from TimestampsSnitch.src.reporting.experiments import report_experiment


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def report_all_experiments():
    experiments = get_all_experiments(experiments_full_endpoint)
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
        experiment = get_document(experiment_name, experiments_full_endpoint)
        if experiment:
            report_experiment(experiment)
