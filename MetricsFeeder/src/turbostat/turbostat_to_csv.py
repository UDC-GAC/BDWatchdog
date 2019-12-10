# Copyright (c) 2019 Universidade da Coruña
# Authors:
#     - Jonatan Enes [main](jonatan.enes@udc.es, jonatan.enes.alvarez@gmail.com)
#     - Roberto R. Expósito
#     - Juan Touriño
#
# This file is part of the BDWatchdog framework, from
# now on referred to as BDWatchdog.
#
# BDWatchdog is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# BDWatchdog is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BDWatchdog. If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function

import socket
import sys
import fileinput
import signal
import subprocess
import time
import traceback


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def sigterm_handler(_signo, _stack_frame):
    good_finish()


def good_finish():
    sys.stdout.flush()
    sys.exit(0)


def bad_finish():
    sys.exit(1)


def get_hostname():
    return socket.gethostname()


def get_timestamp():
    return int(time.time())


def create_header_mapping(header):
    mapping = dict()
    fs = header.split(",")
    counter = 0
    for f in fs:
        mapping[f] = counter
        counter += 1
    return mapping


signal.signal(signal.SIGTERM, sigterm_handler)


def process_line(line, header_mapping, fields):
    if not line:
        eprint("Empty line")
        return

    # Skip header by looking for it and avoiding it
    try:
        # Try to test for string values for different versions of turbostat
        # if fields[0] == "Core" or fields[0] == "Package" or fields[0] == "usec":
        #    continue

        # Try to cast the average Megahertz, which has an int value for all the lines to be processed
        int(fields[header_mapping["Avg_MHz"]])

    except ValueError:
        # Line is header, skip
        return
    except IndexError:
        # Line is ?
        eprint("Error with line:" + line)
        return

    try:
        if fields[header_mapping["CPU"]] == "-":
            # line is for entire system
            return ("SYS_PWR" + "," + get_hostname() + "," + str(get_timestamp()) + "," + fields[
                header_mapping["Core"]] + "," + fields[header_mapping["PkgTmp"]] + "," + fields[
                      header_mapping["PkgWatt"]])
        else:
            if len(fields) >= header_mapping["PkgWatt"]:
                # line is for package, because turbostat aggregates and joins first core
                # and package, print also core
                if "Package" in header_mapping:
                    return ("PKG_PWR" + "," + get_hostname() + "," + str(get_timestamp()) + "," + fields[
                        header_mapping["Package"]] + "," + fields[header_mapping["PkgTmp"]] + "," + fields[
                              header_mapping["PkgWatt"]])

                else:
                    # Host may only have one package and turbostat may not report the Package field
                    return ("PKG_PWR" + "," + get_hostname() + "," + str(get_timestamp()) + "," + fields[
                        header_mapping["Core"]] + "," + fields[header_mapping["PkgTmp"]] + "," + fields[
                              header_mapping["PkgWatt"]])

    except IndexError:
        eprint("Line : '" + line.strip() + "' couldn't be parsed")
        return


def behave_like_pipeline():
    try:
        header_was_processed = False
        #required_fields = ["PkgWatt", "CorWatt", "Core", "CPU"]
        required_fields = ["PkgWatt", "Core", "CPU"]
        header_mapping = dict()

        for line in fileinput.input():
            #print(line)
        #while True:
            #line = sys.stdin.readline()

            fields = line.split(",")

            # Process header and adapt pipe, after that header will be skipped
            if not header_was_processed:
                header_mapping = create_header_mapping(line.strip())
                # print("HEADER MAPPING:" + str(header_mapping))
                for field in required_fields:
                    if field not in header_mapping:
                        eprint("Field " + field + " not present in output, can't continue")
                        bad_finish()
                header_was_processed = True

            # Process line
            else:
                result = process_line(line, header_mapping, fields)
                if result:
                    print(result)

    except KeyboardInterrupt:
        good_finish()
    except Exception as error:
        eprint("[TURBOSTAT TO CSV] error : " + str(error) + str(traceback.format_exc()))

def main():
    behave_like_pipeline()


if __name__ == "__main__":
    main()

# try:
#     header_was_processed = False
#     #required_fields = ["PkgWatt", "CorWatt", "Core", "CPU"]
#     required_fields = ["PkgWatt", "Core", "CPU"]
#     header_mapping = dict()
#
#     for line in fileinput.input():
#         fields = line.split(",")
#
#         # Process header and adapt pipe, after that header will be skipped
#         if not header_was_processed:
#             header_mapping = create_header_mapping(line.strip())
#             # print("HEADER MAPPING:" + str(header_mapping))
#             for field in required_fields:
#                 if field not in header_mapping:
#                     eprint("Field " + field + " not present in output, can't continue")
#                     bad_finish()
#             header_was_processed = True
#
#         # Process line
#         else:
#             # Skip header by looking for it and avoiding it
#             try:
#                 # Try to test for string values for different versions of turbostat
#                 #if fields[0] == "Core" or fields[0] == "Package" or fields[0] == "usec":
#                 #    continue
#
#                 # Try to cast the average Megahertz, which has an int value for all the lines to be processed
#                 int(fields[header_mapping["Avg_MHz"]])
#
#             except ValueError:
#                 # Line is header, skip
#                 continue
#
#             try:
#                 if fields[header_mapping["CPU"]] == "-":
#                     # line is for entire system
#                     print("SYS_PWR" + "," + get_hostname() + "," + str(get_timestamp()) + "," + fields[
#                         header_mapping["Core"]] + "," + fields[header_mapping["PkgTmp"]] + "," + fields[
#                               header_mapping["PkgWatt"]])
#                 else:
#                     if len(fields) >= header_mapping["PkgWatt"]:
#                         # line is for package, because turbostat aggregates and joins first core
#                         # and package, print also core
#                         if "Package" in header_mapping:
#                             print("PKG_PWR" + "," + get_hostname() + "," + str(get_timestamp()) + "," + fields[
#                                 header_mapping["Package"]] + "," + fields[header_mapping["PkgTmp"]] + "," + fields[
#                                       header_mapping["PkgWatt"]])
#
#                         else:
#                             # Host may only have one package and turbostat may not report the Package field
#                             print("PKG_PWR" + "," + get_hostname() + "," + str(get_timestamp()) + "," + fields[
#                                 header_mapping["Core"]] + "," + fields[header_mapping["PkgTmp"]] + "," + fields[
#                                       header_mapping["PkgWatt"]])
#                     #     print("CORE_PWR" + "," + get_hostname() + "," + str(get_timestamp()) + "," + fields[
#                     #         header_mapping["Core"]] + "," + fields[header_mapping["CoreTmp"]].strip())
#                     #
#                     # elif len(fields) >= header_mapping["CoreTmp"]:
#                     #     # line is for core
#                     #     print("CORE_PWR" + "," + get_hostname() + "," + str(get_timestamp()) + "," + fields[
#                     #         header_mapping["Core"]] + "," + fields[header_mapping["CoreTmp"]].strip())
#
#             except IndexError:
#                 eprint("Line : '" + line.strip() + "' couldn't be parsed")
# except KeyboardInterrupt:
#     good_finish()
# except IOError:
#     bad_finish()


