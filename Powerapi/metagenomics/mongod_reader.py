# Copyright (c) 2019 Universidade da Coruña
# Authors:
#     - Jonatan Enes [main](jonatan.enes@udc.es, jonatan.enes.alvarez@gmail.com)
#     - Roberto R. Expósito
#     - Juan Touriño
#
# This file is part of the ServerlessContainers framework, from
# now on referred to as ServerlessContainers.
#
# ServerlessContainers is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# ServerlessContainers is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ServerlessContainers. If not, see <http://www.gnu.org/licenses/>.


import json
import sys

from datetime import datetime
import time
from pymongo import MongoClient


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


missed_data = 0
total_data = 0
partial_data = 0
anomalous_data = 0

MAX_POWER_CAP = 200


def main():
    def dump_target(target):
        global missed_data, total_data, partial_data, anomalous_data

        total_data += 1
        posts = collection.find(
            {"timestamp": {'$lte': dt_end, '$gte': dt_start}, "target": target})
        if posts.count() == 0:
            # eprint("[!!!!] No posts retrieved at {0} for {1}".format(datetime.fromtimestamp(time.time()), target))
            missed_data += 1
            return
        else:
            if posts.count() < 11:
                partial_data += 1

            # eprint(
            #    "[....] {0} posts retrieved at {1} for {2}".format(posts.count(), datetime.fromtimestamp(time.time()),
            #                                                   target))
        power = 0
        num_docs = 0
        for post in posts:
            # pprint.pprint(post)
            if post["metadata"]["scope"] == "cpu":
                power += post["power"]
                num_docs += 1
            collection.delete_one({"_id": post['_id']})
        power /= window_size

        if power > MAX_POWER_CAP:
            # eprint("Value: {0} for container {1} is too large".format(power_string, target))
            anomalous_data += 1
            power = MAX_POWER_CAP

        doc = dict()
        power_string = str(round(power, 2))
        doc["metric"] = "sys.cpu.energy"
        doc["timestamp"] = str(int(end_date + TWO_HOURS))
        doc["value"] = power_string
        doc["tags"] = {"host": target}

        print(json.dumps(doc))

    delay = 10
    TWO_HOURS = 2 * 60 * 60
    start_date = time.time() - TWO_HOURS - delay

    client = MongoClient('mongodb://192.168.52.110:27017/')

    window_size = 5  # seconds

    while True:
        end_date = start_date + window_size
        dt_end = datetime.fromtimestamp(end_date)
        dt_start = datetime.fromtimestamp(start_date)
        start_date += window_size

        # Host4
        db = client['smartwatts4']
        collection = db['power']
        for target in ["pre0", "pre1", "pre2", "pre3"]:
            dump_target(target)
        # Remove all the other documents
        collection.delete_many({"timestamp": {'$lte': dt_end}})

        # Host5
        db = client['smartwatts5']
        collection = db['power']
        for target in ["comp0", "comp1", "comp2", "comp3"]:
            dump_target(target)
        # Remove all the other documents
        collection.delete_many({"timestamp": {'$lte': dt_end}})

        # Host6
        db = client['smartwatts6']
        collection = db['power']
        for target in ["comp4", "comp5", "comp6", "comp7"]:
            dump_target(target)
        # Remove all the other documents
        collection.delete_many({"timestamp": {'$lte': dt_end}})

        # Host7
        db = client['smartwatts7']
        collection = db['power']
        for target in ["comp8", "comp9", "aux0", "aux1"]:
            dump_target(target)
        # Remove all the other documents
        collection.delete_many({"timestamp": {'$lte': dt_end}})

        time_now = time.time()

        if end_date >= time_now - TWO_HOURS - delay:
            eprint("Data points accounting is [total | partial | anomalous | missed ] " +
                   " {0},{1},{2},{3} ".format(total_data, partial_data, anomalous_data, missed_data) +
                   "ratios are [{0},{1},{2}]".format(
                       str(int(100 * partial_data / total_data)),
                       str(int(100 * anomalous_data / total_data)),
                       str(int(100 * missed_data / total_data))
                   )
                   )
            time.sleep(window_size)


if __name__ == "__main__":
    main()
