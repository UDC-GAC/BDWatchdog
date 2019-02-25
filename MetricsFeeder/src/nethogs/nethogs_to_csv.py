#!/usr/bin/env python
from __future__ import print_function
import sys
import pwd
import subprocess
import socket
import signal

timestamp = 0
interval = 0


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def sigterm_handler(_signo, _stack_frame):
    good_finish()


def good_finish():
    sys.stdout.flush()
    sys.exit(0)


def bad_finish(error):
    eprint("[ATOP TO CSV] error in : " + str(error))
    sys.exit(1)


signal.signal(signal.SIGTERM, sigterm_handler)


def process_line(line):
    global timestamp
    global interval
    if line.startswith("TIMESTAMP:"):
        timestamp = int(line.strip().split(":")[1])
        return None
    if line.startswith("INTERVAL:"):
        interval = int(line.strip().split(":")[1])
        return None
    if line == "\n" or line == "" or line.startswith("END") or line.startswith("START"):
        return None

    try:
        fields = line.split()
        command_string = ''.join(fields[0:len(fields) - 2])
        out_bandwidth = float(fields[-2])
        in_bandwidth = float(fields[-1])
        fields = command_string.split("/")
        uid = int(fields[-1])
        username = pwd.getpwuid(uid).pw_name
        pid = int(fields[-2])
    except (IndexError, ValueError):
        return None

    if pid == 0:
        return None

    try:
        result = subprocess.check_output(['ps', '-p', str(pid), '-o', 'comm='])
    except subprocess.CalledProcessError:
        return None
    command = "(" + result.strip() + ")"
    hostname = socket.gethostname()
    header = "NETHOGS"

    return (header + "," + hostname + "," + str(timestamp) + "," + str(
        interval) + "," + username + "," + command + "," + str(pid) + "," + str(
        out_bandwidth) + "," + str(in_bandwidth))


def behave_like_pipeline():
    try:
        # for line in fileinput.input():
        while True:
            line = sys.stdin.readline()
            try:
                result = process_line(line)
                if result:
                    print(result)
            except (KeyboardInterrupt, IOError):
                # Exit silently
                pass
            except Exception as e:
                eprint("ERROR in line '" + line.strip() + "'")
                eprint(e)
    except KeyboardInterrupt:
        # Exit silently
        good_finish()
    except IOError as e:
        bad_finish(e)


def main():
    behave_like_pipeline()


if __name__ == "__main__":
    main()
