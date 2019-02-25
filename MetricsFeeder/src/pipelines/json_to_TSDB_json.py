#!/usr/bin/env python
from __future__ import print_function
import sys
import json
import re


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def process_string(string):
    string = string.replace("(", "")
    string = string.replace(")", "")
    m = re.search(r"([A-Za-z0-9_,:\\/\s]+)", string)
    matched = m.group(1)
    pat_list = re.findall("\w+", matched)
    # If there are multiple words
    if len(pat_list) > 1:
        new_match = matched
        new_match = new_match.replace("[", "")
        new_match = new_match.replace("]", "")
        new_match = new_match.replace("{", "")
        new_match = new_match.replace("}", "")
        new_match = new_match.replace("-", "_hyphen_")
        new_match = new_match.replace("=", "_equals_")
        new_match = new_match.replace(".", "_dot_")
        new_match = new_match.replace("*", "_asterisk_")
        new_match = new_match.replace(">", "_right_arrow_")
        new_match = new_match.replace("<", "_left_arrow_")
        new_match = new_match.replace(",", "_comma_")
        new_match = new_match.replace(":", "_twodot_")
        new_match = new_match.replace("/", "_slash_")
        new_match = new_match.replace(" ", "_space_")
        string = string.replace(matched, new_match)
    return string


def process_line(line):
    document = json.loads(line)
    try:
        for string in ["command", "host"]:
            if string in document["tags"]:
                document["tags"][string] = process_string(document["tags"][string])

        return json.dumps(document)
    except Exception:
        # If any error, just dump the original document
        return json.dumps(document)


def behave_like_pipeline():
    try:
        # for line in fileinput.input():
        while True:
            line = sys.stdin.readline()
            print(process_line(line))
    except (KeyboardInterrupt, IOError):
        # Exit silently
        pass
    except Exception as e:
        eprint("[JSON TO VALID_JSON] error: " + str(e))


def main():
    behave_like_pipeline()


if __name__ == "__main__":
    main()
