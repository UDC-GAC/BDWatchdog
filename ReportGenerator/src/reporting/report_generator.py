#!/usr/bin/env python
from __future__ import print_function

import sys
import time

from ReportGenerator.src.reporting.experiments import report_experiment
from TimestampsSnitch.src.mongodb.mongodb_agent import MongoDBTimestampAgent


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


agent = MongoDBTimestampAgent()


def report_all_experiments():
    experiments = agent.get_all_experiments()
    if experiments:
        for exp in experiments:
            time_start = time.time()
            report_experiment(exp)
            time_end = time.time()
            eprint("Reporting of experiment {0} took {1} seconds".format(exp["experiment_name"], time_end - time_start))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Must specicy an experiment name or ALL")
    else:
        experiment_name = sys.argv[1]
        if experiment_name == "ALL":
            report_all_experiments()
        else:
            experiment = agent.get_experiment(experiment_name)
            if experiment:
                report_experiment(experiment)
            else:
                eprint("No experiment '{0}' found".format(experiment_name))
