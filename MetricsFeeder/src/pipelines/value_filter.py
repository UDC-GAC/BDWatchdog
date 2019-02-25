#!/usr/bin/env python
import sys


def process_line(line):
    in_fields = line.split(",")

    # Let always a single process through so as to give always at least one metric for process-based monitoring,
    # otherwise if there are no usages they will be all filtered out by the value filter (due to too low values)
    # thus giving the impression of non-usage
    command = in_fields[5]
    if command == "(systemd)":
        return line.strip()

    if in_fields[0] == "PRM":
        if float(in_fields[6]) < 10.0:
            return  # virtual
        if float(in_fields[7]) < 10.0:
            return  # resident
    if in_fields[0] == "PRC":
        if float(in_fields[7]) + float(in_fields[8]) + float(in_fields[9]) < 0.05:
            return  # sys + user + wait
    if in_fields[0] == "PRD":
        if float(in_fields[7]) + float(in_fields[8]) < 0.05:
            return  # MB read + write bandwidth
    if in_fields[0] == "PRN":
        if int(in_fields[7]) + int(in_fields[9]) + int(in_fields[11]) + int(in_fields[13]) < 30:
            return  # TCP and UDP packets in and out
        if float(in_fields[8]) + float(in_fields[10]) + float(in_fields[12]) + float(in_fields[14]) < 0.05:
            return  # TCP and UDP MB bandwidths in and out
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


def main():
    behave_like_pipeline()


if __name__ == "__main__":
    main()
