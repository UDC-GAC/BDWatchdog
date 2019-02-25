#!/usr/bin/env python
import fileinput

first_batch_processed = False
in_second_batch = False

for line in fileinput.input():
    if line.startswith("START") or line.startswith("TIMESTAMP") \
            or line.startswith("INTERVAL"):
        print(line.strip())

    elif line.startswith("Refreshing:"):
        if not first_batch_processed:
            first_batch_processed = True
        else:
            in_second_batch = True
    elif line.startswith("END"):
        first_batch_processed = False
        in_second_batch = False
    else:
        if in_second_batch:
            print(line.strip())

