# Copyright (c) 2019 Universidade da Coruña
# Authors:
#     - Jonatan Enes [main](jonatan.enes@udc.es, jonatan.enes.alvarez@gmail.com)
#     - Roberto R. Expósito
#     - Juan Touriño
#
# This file is part of the ServerlessContainers framework, from
# now on referred to as ServerlessContainers.
#
# ServerlessContainers is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# ServerlessContainers is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ServerlessContainers. If not, see <http://www.gnu.org/licenses/>.


from __future__ import print_function

import argparse
import sys
import json

from TimestampsSnitch.src.mongodb.mongodb_agent import MongoDBTimestampAgent


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def print_experiment(experiment_data):
    doc_to_dump = {"type": "experiment", "info": {}}
    for field in ["username", "start_time", "end_time", "experiment_id"]:
        if field not in experiment_data:
            eprint("Field {0} missing from experiment {1}".format(field, experiment_data["experiment_id"]))
        else:
            doc_to_dump["info"][field] = experiment_data[field]
    print(json.dumps(doc_to_dump))


if __name__ == '__main__':
    mongodb_agent = MongoDBTimestampAgent()

    parser = argparse.ArgumentParser(description='Get test information of a particular experiment')
    parser.add_argument('experiment_name', metavar='experiment_name', type=str,
                        help='The name of the experiment to be retrieved or "ALL" in all the experiments are to be retrieved')

    args = parser.parse_args()

    if args.experiment_name == "ALL":
        data = mongodb_agent.get_all_experiments()
        if not data:
            eprint("Couldn't find experiment data, maybe there is none?")
    else:
        data = mongodb_agent.get_document(args.experiment_name)
        if not data:
            eprint("Couldn't find experiment with id {0}".format(args.experiment_name))

    if not data:
        exit(0)

    if type(data) == type(dict()):
        print_experiment(data)
    elif type(data) == type(list()):
        for experiment in data:
            print_experiment(experiment)
    else:
        print_experiment(data)
