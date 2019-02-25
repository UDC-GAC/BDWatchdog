#!/usr/bin/env python
from __future__ import print_function
import sys


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def process_line(line):
    in_fields = line.split(",")

    # Use this filter to drop processes of kernel OS when the -a atop option is present
    if in_fields[0] in ["PRC", "PRN", "PRM"]:
        if any(command in in_fields[5] for command in
               ["(kworker)", "(systemd)", "(migration)", "(rcu)", "(ksoftirq)", "(bioset)"]):
            return

    # FIX for very high disk values of terminal process probably due to pseudo writes of the use of pipelines
    if in_fields[0] == "PRD":
        if any(command in in_fields[5] for command in
               ["(nethogs), (python), (kworker)", "(migration)", "(rcu)",
                "(ksoftirq)", "(bash)", "(bioset)", "(sshd)", "(ssh)"]):
            return
    return line.strip()


def behave_like_pipeline():
    try:
        # for line in fileinput.input():
        while True:
            line = sys.stdin.readline()
            result = process_line(line)
            if result:
                print(result)
    except (KeyboardInterrupt, IOError):
        # Exit silently
        pass
    except Exception as error:
        eprint("[CUSTOM FILTER] error : " + str(error))


def main():
    behave_like_pipeline()


if __name__ == "__main__":
    main()
