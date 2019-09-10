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
import sys
import os
import subprocess
import signal
from daemon import runner
import socket

import MetricsFeeder.src.daemons.daemon_utils as daemon_utils
from MetricsFeeder.src.daemons.daemon_utils import MonitoringDaemon

SERVICE_NAME = "Turbostat_" + str(socket.gethostname())

_base_path = os.path.dirname(os.path.abspath(__file__))

config_path = "conf/turbostat_config.ini"

config_keys = [
    "TURBOSTAT_SAMPLING_FREQUENCY",
    "POST_ENDPOINT_PATH",
    "POST_DOC_BUFFER_TIMEOUT",
    "PYTHONUNBUFFERED",
    "TEMPLATE_PATH",
    "METRICS_PATH",
    "TAGS_PATH",
    "POST_DOC_BUFFER_LENGTH",
    "POST_SEND_DOCS_TIMEOUT",
    "POST_SEND_DOCS_FAILED_TRIES",
    "HEARTBEAT_ENABLED"
]

default_environment_values = {
    "TURBOSTAT_SAMPLING_FREQUENCY": "5",
    "POST_ENDPOINT_PATH": "http://opentsdb:4242/api/put",
    "POST_DOC_BUFFER_TIMEOUT": "30",
    "PYTHONUNBUFFERED": "yes",
    "TEMPLATE_PATH": os.path.join(_base_path, "../pipelines/templates/"),
    "METRICS_PATH": os.path.join(_base_path, "../pipelines/metrics/"),
    "TAGS_PATH": os.path.join(_base_path, "../pipelines/tags/"),
    "POST_DOC_BUFFER_LENGTH": "1000",  # Don't go over 1500 or post packet will be too large and may cause error
    "POST_SEND_DOCS_TIMEOUT": "10",
    "POST_SEND_DOCS_FAILED_TRIES": "6",
    "HEARTBEAT_ENABLED": False
}


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def turbostat_is_runnable(environment):
    # Run a bogus 'ls' command with turbostat statistics
    # If the command doesn't fail, turbostat works
    return daemon_utils.command_is_runnable(['turbostat', 'ls'])



class Turbostat(MonitoringDaemon):
    def run(self):
        self.launch_pipeline()
        self.launch_heartbeat()
        self.loop()

    def create_pipeline(self):
        processes_list = []

        # Create the data source
        turbostat = subprocess.Popen([
            'turbostat',
            '-i',
            self.environment["TURBOSTAT_SAMPLING_FREQUENCY"],
            # '--processor' # variable not longer recognized although the manual still reports it in the latest versions
            ],
            stdout=subprocess.PIPE)
        processes_list.append(turbostat)

        # Create the data pipeline
        first_sed = self.create_pipe([
            'sed',
            '-u',
            '-e',
            's/^[ \t]*//'
        ], self.environment, turbostat.stdout, subprocess.PIPE)
        processes_list.append(first_sed)

        second_sed = self.create_pipe([
            'sed',
            '-u',
            '-e',
            's/[[:space:]]\+/,/g'
        ], self.environment, first_sed.stdout, subprocess.PIPE)
        processes_list.append(second_sed)

        turbostat_to_csv = self.create_pipe([os.path.join(_base_path, "../turbostat/turbostat_to_csv.py")],
                                            self.environment, second_sed.stdout, subprocess.PIPE)
        processes_list.append(turbostat_to_csv)

        csv_to_json = self.create_pipe([os.path.join(_base_path, "../pipelines/csv_to_json.py")],
                                       self.environment, turbostat_to_csv.stdout, subprocess.PIPE)
        processes_list.append(csv_to_json)

        json_to_tsdb_json = self.create_pipe([os.path.join(_base_path, "../pipelines/json_to_TSDB_json.py")],
                                             self.environment, csv_to_json.stdout, subprocess.PIPE)
        processes_list.append(json_to_tsdb_json)

        send_to_opentsdb = self.create_pipe([os.path.join(_base_path, "../pipelines/send_to_OpenTSDB.py")],
                                            self.environment, json_to_tsdb_json.stdout, subprocess.PIPE)
        processes_list.append(send_to_opentsdb)

        return processes_list


if __name__ == '__main__':
    handler, logger = daemon_utils.configure_daemon_logs(SERVICE_NAME)

    app = Turbostat(SERVICE_NAME, logger)
    # FIXME As part of the environment initilization, set the pythonpath correctly
    app.initialize_environment(config_path, config_keys, default_environment_values)
    app.is_runnable = turbostat_is_runnable
    app.not_runnable_message = "Turbostat program is not runnable, if it is installed, run the " + \
                               "'scripts/allow_turbostat.sh' and try again or run turbostat manually and check " \
                               "for errors.\n" + \
                               "Also, remember that programs like turbostat can't be executed on virtual " + \
                               "machine due to their need of hardware assisted technologies."

    app.check_if_runnable()

    # Capture reload signal and propagate
    signal.signal(signal.SIGHUP, app.reload_pipeline)

    # Run service
    serv = runner.DaemonRunner(app)
    serv.daemon_context.files_preserve = [handler.stream]
    serv.do_action()
