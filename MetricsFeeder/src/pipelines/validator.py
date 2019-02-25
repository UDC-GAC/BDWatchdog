#!/usr/bin/env python
from __future__ import print_function
import sys


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


lengths_map = {
    "CPU": 13,
    "cpu": 11,
    "MEM": 6,
    "SWP": 6,
    "DSK": 10,
    "NET": 11,
    "PRC": 10,
    "PRM": 8,
    "PRD": 9,
    "PRN": 15,
    "INFINIBAND": 8
}

integer_fields = {
    "CPU": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    "cpu": [2, 3, 4, 5, 6, 7, 8, 9, 10],
    "MEM": [2, 3, 4, 5],
    "SWP": [2, 3, 4, 5],
    "DSK": [2, 3, 5, 6, 7, 8, 9],
    "NET": [2, 3, 5, 6, 7, 8, 9, 10],
    "PRC": [2, 3, 4, 7, 8, 9],
    "PRM": [2, 3, 6, 7],
    "PRD": [2, 3, 4, 7, 8],
    "PRN": [2, 3, 4, 7, 8, 9, 10, 11, 12, 13, 14],
    "INFINIBAND": [2, 3, 6, 7]
}


def check_length(line):
    fields = line.split(",")
    header = fields[0]
    if len(fields) != lengths_map[header]:
        return False
    return True


def check_state_field(field):
    if len(field) == 0:
        return False
    elif len(field) > 1:
        return False
    else:
        return True


def check_int_field(field):
    try:
        _ = int(field)
        return True
    except ValueError:
        return False


def process_line(line):
    fields = line.split(",")
    header = fields[0]
    line_passes = True

    if not check_length(line):
        eprint("[VALIDATOR] line doesn't pass length checks: '" + line.strip() + "'")
        return None

    for field_num in integer_fields[header]:
        if not check_int_field(fields[field_num]):
            line_passes = False
            break

    if header == "PRC" or header == "PRN" or header == "PRD":
        if not check_state_field(fields[6]):
            line_passes = False

    if header == "PRM":
        if not check_state_field(fields[5]):
            line_passes = False

    if line_passes:
        return line.strip()
    else:
        eprint("[VALIDATOR] line doesn't pass field checks: '" + line.strip() + "'")
        return None


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
    except Exception as e:
        eprint("[VALIDATOR] error: " + str(e))


def main():
    behave_like_pipeline()


if __name__ == "__main__":
    main()
