#!/usr/bin/env python
from __future__ import print_function
import requests
import time
import json
import os
import signal
import sys

## ENVIRONMENT VARIABLES ##

default_experiment_id = "experiment_0"

default_resourcemanager_ip = "master"
default_resourcemanager_port = 8088

RESOURCEMANAGER_IP = "RESOURCEMANAGER_IP"
resourcemanager_ip = os.getenv(RESOURCEMANAGER_IP, default_resourcemanager_ip)

RESOURCEMANAGER_PORT = "RESOURCEMANAGER_PORT"
try:
    resourcemanager_port = str(int(os.getenv(RESOURCEMANAGER_PORT, default_resourcemanager_port)))
except ValueError:
    resourcemanager_port = default_resourcemanager_port

ResourceManager_endpoint = 'http://' + resourcemanager_ip + ':' + resourcemanager_port + '/ws/v1/cluster/apps'

unfinished_apps = list()
polling_interval = 10  # in seconds

_base_path = os.path.dirname(os.path.abspath(__file__))

default_experiment_id = "experiment_0"
default_experiment_id_path = os.path.join(_base_path, "../experiment_id.txt")

EXPERIMENT_ID_FILE_PATH = "EXPERIMENT_ID_FILE_PATH"
experiment_id_path = os.getenv(EXPERIMENT_ID_FILE_PATH, default_experiment_id_path)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def reload_experiment_id(_signo, _stack_frame):
    global experiment_id
    eprint("[YARN SNITCH] Signal caught to reload")
    flush_tests_before_experiment_reload()
    experiment_id = get_experiment_id()
    eprint("[YARN SNITCH] New experiment id is : " + experiment_id)


def flush_tests_before_experiment_reload():
    eprint("[YARN SNITCH] On-demand polling before reloading experiment_id")
    poll()


signal.signal(signal.SIGHUP, reload_experiment_id)


def get_experiment_id():
    try:
        with open(experiment_id_path, "r") as myfile:
            data = myfile.readlines()
        if not data:
            return default_experiment_id
        experiment_id = data[0].strip()
    except IOError:
        return default_experiment_id
    return experiment_id


def merge_new_finished_apps(retrieved_apps, apps_dict):
    new_apps_found = dict()
    for key in retrieved_apps:
        if key in apps_dict.keys():
            pass
        else:
            new_app = retrieved_apps[key]
            if not app_is_unfinished(new_app):
                new_apps_found[key] = new_app
                apps_dict[key] = new_app
    return apps_dict, new_apps_found


def get_yarn_apps():
    retrieved_apps = dict()
    try:
        r = requests.get(ResourceManager_endpoint)
        if r.status_code == 200:
            response = r.json()
            apps = response["apps"]
            if apps:
                for app in apps["app"]:
                    retrieved_apps[app["id"]] = app
        else:
            eprint(
                "[YARN SNITCH] Couldn't poll for new apps in endpoint " + ResourceManager_endpoint + " at " + time.strftime(
                    "%D %H:%M:%S", time.localtime()))
    except requests.exceptions.ConnectionError:
        eprint(
            "[YARN SNITCH] Couldn't poll for new apps in endpoint " + ResourceManager_endpoint + " at " + time.strftime(
                "%D %H:%M:%S", time.localtime()))

    return retrieved_apps


def write_piece_of_information(experiment_id, username, app_id, app_name, app_start_time, app_end_time):
    d = dict()

    info = dict()
    info["experiment_id"] = experiment_id
    info["username"] = username
    info["test_id"] = app_id
    info["start_time"] = app_start_time / 1000
    info["end_time"] = app_end_time / 1000
    info["test_name"] = app_name

    d["info"] = info
    d["type"] = "test"

    print(json.dumps(d))


def snitch_apps_dict(apps):
    for key in apps:
        app = apps[key]
        snitch_an_app(app)


def snitch_an_app(app):
    if not app_is_unstarted(app) and not app_is_unfinished(app):
        write_piece_of_information(experiment_id, app["user"], app["id"], app["name"], app["startedTime"],
                                   app["finishedTime"])


def app_is_unstarted(app):
    return app["startedTime"] == 0


def app_is_unfinished(app):
    return app["finishedTime"] == 0


def poll():
    global apps_dict
    retrieved_apps = get_yarn_apps()
    if retrieved_apps == {}:
        # Error in polling
        pass
    else:
        apps_dict, new_finished_apps_found = merge_new_finished_apps(retrieved_apps, apps_dict)
        if not new_finished_apps_found == {}:
            eprint("[YARN SNITCH] New finished apps detected, going to snitch on them")
            snitch_apps_dict(new_finished_apps_found)


experiment_id = get_experiment_id()
eprint(
    "[YARN SNITCH] Snitch has started, monitoring '" + str(ResourceManager_endpoint) + "' with an interval of '" + str(
        polling_interval) + "' seconds.")
apps_dict = get_yarn_apps()
# eprint("Initial detected apps, going to snitch on them")
# eprint(json.dumps(apps_dict))
# snitch_apps_dict(apps_dict)
try:
    while True:
        poll()
        time.sleep(polling_interval)
except KeyboardInterrupt:
    eprint("[YARN SNITCH] terminated")
