#!/usr/bin/env python
import sys
import os
import subprocess
import time
import signal
import logging
from daemon import runner
import configparser
from threading import Thread
import errno

_base_path = os.path.dirname(os.path.abspath(__file__))

config_keys = [
    "PYTHONUNBUFFERED",
    "RESOURCEMANAGER_IP",
    "RESOURCEMANAGER_PORT",
    "MONGODB_IP",
    "MONGODB_PORT"
]

default_environment_values = {
    "PYTHONUNBUFFERED": "yes",
    "RESOURCEMANAGER_IP" : "master",
    "RESOURCEMANAGER_PORT" : "8088",
    "MONGODB_IP" : "bdwatchdog",
    "MONGODB_PORT": "8000"
}

service_name = "YarnSnitch"


def check_path_existance_and_create(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def create_environment(config_dict):
    custom_environment = os.environ.copy()

    ## FROM CONFIG FILE ##
    for key in config_keys:
        if key in config_dict.keys():
            custom_environment[key] = config_dict[key]
        else:
            custom_environment[key] = default_environment_values[key]

    return custom_environment


def createPipe(commandArray, environment, pipe_input, pipe_output):
    return subprocess.Popen(commandArray,
                            env=environment,
                            stdin=pipe_input,
                            stdout=pipe_output
                            )


def good_finish():
    sys.exit(0)


def bad_finish():
    sys.exit(1)


def read_config():
    config_dict = {}
    config = configparser.ConfigParser()
    config.read(os.path.join(_base_path, "conf/yarn-snitch.ini"))
    for key in config_keys:
        try:
            config_dict[key] = config['DEFAULT'][key]
        except KeyError:
            pass  # Key is not configure, take the default value
    return config_dict


# Terminate all the programs that create the pipeline
def destroy_pipeline(processess_list):
    logger.info("Destroying pipeline")
    for process in processess_list:
        try:
            process.terminate()
            process.wait()
            logger.info("Process " + str(process.pid) + " terminated with exit status " + str(process.returncode))
        except OSError:
            # Process may have already exited
            pass


def create_pipeline():
    processess_list = []

    custom_environment = create_environment(read_config())

    yarn_snitch = subprocess.Popen([os.path.join(_base_path, "scripts/yarn-snitch.py")], stdout=subprocess.PIPE,
                                   env=custom_environment)
    processess_list.append(yarn_snitch)

    mongodb_agent = createPipe([os.path.join(_base_path, "scripts/mongodb_agent.py")], custom_environment,
                               yarn_snitch.stdout, subprocess.PIPE)
    processess_list.append(mongodb_agent)

    return processess_list


def poll_for_exited_processess(processess_list):
    for process in processess_list:
        process.poll()
        if process.returncode is not None:
            return True
    return False


class YarnSnitch():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = os.path.join(_base_path, "logs/"+service_name+".out")
        self.stderr_path = os.path.join(_base_path, "logs/"+service_name+".err")
        self.pidfile_path = os.path.join(_base_path, "pids/"+service_name+".pid")
        self.pidfile_timeout = 5
        self.pipeline_tries = 0
        self.MAX_TRIES = 5
        self.processess_list = []

    def reload_pipeline(self, _signo, _stack_frame):
        logger.info("going to reload pipeline")
        destroy_pipeline(self.processess_list)
        self.processess_list = create_pipeline()

    def threaded_read_last_process_output(self, process, logger):
        for line in process.stdout:
            # logger.info(line.strip()) # Dump to log file
            print(line.strip())  # Dump to stdout of daemon
            sys.stdout.flush()

    def run(self):
        logger.info("Launching pipeline")
        self.processess_list = create_pipeline()

        ## Launch thread to log last process output
        thread = Thread(target=self.threaded_read_last_process_output, args=(self.processess_list[-1], logger))
        thread.start()
        self.dumper_thread = thread

        try:
            while True:
                exited_processess = poll_for_exited_processess(self.processess_list)
                if (not exited_processess):
                    pass
                else:
                    logger.info("Error in pipeline")
                    destroy_pipeline(self.processess_list)
                    if (self.pipeline_tries < self.MAX_TRIES):
                        self.pipeline_tries += 1
                        logger.info("The pipeline was destroyed, re-creating and launching a new one")
                        processess_list = create_pipeline()

                        ## Launch thread to log last process output
                        thread = Thread(target=self.threaded_read_last_process_output,
                                        args=(self.processess_list[-1], logger))
                        thread.start()
                        self.dumper_thread = thread

                    else:
                        logger.info("Pipeline failed too many times, (" + str(self.MAX_TRIES) + "), stopping daemon")
                        bad_finish()
                time.sleep(5)
        except(SystemExit, KeyboardInterrupt):
            logger.info("Exception or signal caught, stopping daemon and destroying the pipeline.")
            destroy_pipeline(self.processess_list)
            good_finish()


if __name__ == '__main__':
    app = YarnSnitch()
    signal.signal(signal.SIGHUP, app.reload_pipeline)
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(message)s")

    log_path = os.path.join(_base_path, "logs/")
    check_path_existance_and_create(log_path)
    pids_path = os.path.join(_base_path, "pids/")
    check_path_existance_and_create(pids_path)

    handler = logging.FileHandler(os.path.join(log_path, service_name + ".log"))
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    serv = runner.DaemonRunner(app)
    serv.daemon_context.files_preserve = [handler.stream]
    serv.do_action()
