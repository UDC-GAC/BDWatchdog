#!/usr/bin/env python
import fileinput

for line in fileinput.input():
    fields = line.strip().split(" ")
    pid = fields[0]
    for field in fields:
        if field.startswith("org.apache.hadoop.") or field.startswith("org.apache.spark."):
            # print "Process " + pid + " is java with cmdline " + field.strip().split(".")[-1]
            print pid + " " + field.strip().split(".")[-1]
