#!/usr/bin/env python
from __future__ import print_function
import sys
import fileinput
import signal


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
    return line.replace(" ", ",").strip()


def behave_like_pipeline():
    try:
        skip_lines = True
        for line in fileinput.input():
            # FIRST LINES RESTRICTOR
            if line == "SEP\n":
                skip_lines = False
                continue

            # MOST RESTRICTIVE FILTERS
            if line.endswith("n\n") or line.endswith("n 0\n") or skip_lines:
                continue

            print(process_line(line))
    except KeyboardInterrupt:
        # Exit silently
        good_finish()
    except IOError as e:
        bad_finish(e)


def main():
    behave_like_pipeline()


if __name__ == "__main__":
    main()
