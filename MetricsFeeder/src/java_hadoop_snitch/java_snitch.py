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

import subprocess
import time
import pickle
import os
import errno

JAVA_MAPPINGS_FOLDER_PATH = "JAVA_MAPPINGS_FOLDER_PATH"
JAVA_SNITCH_POLLING_SECONDS = "JAVA_SNITCH_POLLING_SECONDS"
HADOOP_SNITCH_FOLDER_PATH = "HADOOP_SNITCH_FOLDER_PATH"
JAVA_SNITCH_TIME_TO_DUMP_COUNTER_MAX = "JAVA_SNITCH_TIME_TO_DUMP_COUNTER_MAX"

_base_path = os.path.dirname(os.path.abspath(__file__))

java_mappings_folder_path = os.getenv(JAVA_MAPPINGS_FOLDER_PATH, os.path.join(_base_path, "../pipelines/java_mappings/"))
java_snitch_polling_seconds = int(os.getenv(JAVA_SNITCH_POLLING_SECONDS, 3))
pipes_folder_path = os.getenv(HADOOP_SNITCH_FOLDER_PATH, os.path.join(_base_path, "../java_hadoop_snitch/"))
time_to_dump_counter_max = int(os.getenv(JAVA_SNITCH_TIME_TO_DUMP_COUNTER_MAX, 2))

process_names = ["NameNode", "SecondaryNameNode", "DataNode", "ResourceManager", "NodeManager", "YarnChild",
                 "MRAppMaster", "CoarseGrainedExecutorBackend"]
process_files = ["NameNode", "SecondaryNameNode", "DataNode", "ResourceManager", "NodeManager", "YarnChild",
                 "MRAppMaster", "CoarseGrainedExecutorBackend", "OTHER"]


def run_command(c):
    """given shell command, returns communication tuple of stdout and stderr"""
    return subprocess.Popen(c,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            stdin=subprocess.PIPE).communicate()


def check_path_existence_and_create(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def read_process_pids_from_file(process_name):
    try:
        with open(java_mappings_folder_path + process_name + '.txt', 'r') as content_file:
            itemlist = pickle.load(content_file)
        return [int(x) for x in itemlist]
    except IOError:
        return []


def read_all():
    proc_dict = dict()
    for proc_file in process_files:
        pids = read_process_pids_from_file(proc_file)
        proc_dict[proc_file] = pids
    return proc_dict


def dump_process_pids_to_file(process_name, pidlist):
    try:
        with open(java_mappings_folder_path + process_name + '.txt', 'w+') as f1:
            pickle.dump([int(x) for x in pidlist], f1)
    except IOError:
        # mapping folder doesn't exist, create it for next time
        check_path_existence_and_create(java_mappings_folder_path)


def merge_lists(l1, l2):
    return list(set(l1 + l2))


def merge_dicts(dict1, dict2):
    # print "Merging dictionaries"
    # print "Dict 1 is: " + str(dict1)
    # print "Dict 2 is: " + str(dict2)
    for key in dict2:
        try:
            dict1[key] = merge_lists(dict1[key], dict2[key])
        except KeyError:
            dict1[key] = dict2[key]
    # print "New dict is " + str(dict1)
    return dict1


def dump_all(java_dict):
    existing_data = read_all()
    java_dict = merge_dicts(java_dict, existing_data)
    print("Dumping dictionaries " + str(java_dict))
    for key in java_dict:
        dump_process_pids_to_file(key, java_dict[key])


def main():

    time_to_dump_counter = 0
    print("[HADOOP JAVA SNITCH] Going to monitor hadoop java process every '" + str(
        java_snitch_polling_seconds) + "' seconds dumping every '" + str(
        java_snitch_polling_seconds * time_to_dump_counter_max) + "' seconds")

    while True:
        java_proc_dict = dict()
        try:
            # lineas = run_command('jps')[0].strip().split('\n')
            cmd = "ps h -eo pid,cmd | " + pipes_folder_path + "java_ps.py"
            ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            lines = ps.communicate()[0].strip().split('\n')
            for line in lines:
                if line == "":
                    continue
                pid_command = line.split(" ")
                pid = pid_command[0]
                command = pid_command[1]
                if command.strip() in process_names:
                    try:
                        pid_list = java_proc_dict[command]
                        pid_list.append(int(pid))
                    except KeyError:
                        java_proc_dict[command] = [int(pid)]
                else:
                    try:
                        pid_list = java_proc_dict["OTHER"]
                        pid_list.append(int(pid))
                    except KeyError:
                        java_proc_dict["OTHER"] = [int(pid)]

            time_to_dump_counter += 1

            time.sleep(java_snitch_polling_seconds)

            if time_to_dump_counter >= time_to_dump_counter_max:
                time_to_dump_counter = 0
                dump_all(java_proc_dict)
                java_proc_dict = dict()

        except KeyboardInterrupt:
            dump_all(java_proc_dict)
            java_proc_dict = dict()
            exit(0)

if __name__ == "__main__":
    main()
