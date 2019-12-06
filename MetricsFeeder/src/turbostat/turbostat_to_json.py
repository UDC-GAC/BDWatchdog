# Copyright (c) 2019 Universidade da Coruña
# Authors:
#     - Jonatan Enes [main](jonatan.enes@udc.es, jonatan.enes.alvarez@gmail.com)
#     - Roberto R. Expósito
#     - Juan Touriño
#
# This file is part of the BDWatchdog framework, from
# now on referred to as BDWatchdog.
#
# BDWatchdog is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# BDWatchdog is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BDWatchdog. If not, see <http://www.gnu.org/licenses/>.


from __future__ import print_function

import fileinput
import sys
import MetricsFeeder.src.turbostat.turbostat_to_csv as turbostat_to_csv

from MetricsFeeder.src.pipelines import csv_to_json as csv_to_json
from MetricsFeeder.src.pipelines import json_to_TSDB_json as json_to_TSDB_json


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def sigterm_handler(_signo, _stack_frame):
    good_finish()


def good_finish():
    sys.stdout.flush()
    sys.exit(0)


def bad_finish(error):
    eprint("[TURBOSTAT TO JSON] error in : " + str(error))
    sys.exit(1)


def process_line(line, metrics_dict, tags_dict, template):
    line_in_csv = turbostat_to_csv.process_line(line)
    if line_in_csv:
        for json in csv_to_json.process_line(line_in_csv, metrics_dict, tags_dict, template):
            TSDB_json = json_to_TSDB_json.process_line(json)
            print(TSDB_json)
    #pass

def behave_like_pipeline():
    global process_function
    try:
        metrics_dict, tags_dict, template = csv_to_json.initialize()

        #while True:
        #    line = sys.stdin.readline()
        #    process_function(line, metrics_dict, tags_dict, template)

        for line in fileinput.input():
           process_function(line, metrics_dict, tags_dict, template)


        # for line in sys.stdin:
        #    process_function(line, metrics_dict, tags_dict, template)

    except KeyboardInterrupt:
        # Exit silently
        good_finish()
    except IOError as e:
        bad_finish(e)


def main():
    behave_like_pipeline()


if __name__ == "__main__":
    main()
