import json
import sys

from datetime import datetime
import time
import pprint
from pymongo import MongoClient


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


missed_data = 0
total_data = 0
partial_data = 0
anomalous_data = 0

MAX_POWER_CAP = 100

def main():
    def dump_target(target):
        global missed_data, total_data, partial_data, anomalous_data

        total_data += 1
        posts = collection.find(
            {"timestamp": {'$lte': dt_end, '$gte': dt_start}, "target": target})
        if posts.count() == 0:
            #eprint("[!!!!] No posts retrieved at {0} for {1}".format(datetime.fromtimestamp(time.time()), target))
            missed_data += 1
            return
        else:
            if posts.count() < 20:
                partial_data += 1

            #eprint(
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
            #eprint("Value: {0} for container {1} is too large".format(power_string, target))
            anomalous_data += 1
            power = MAX_POWER_CAP

        doc = dict()
        power_string = str(round(power, 2))
        doc["metric"] = "sys.cpu.energy"
        doc["timestamp"] = str(int(end_date + TWO_HOURS))
        doc["value"] = power_string
        doc["tags"] = {"host": target}

        print(json.dumps(doc))

    delay = 20
    TWO_HOURS = 2 * 60 * 60
    start_date = time.time() - TWO_HOURS - delay

    client = MongoClient('mongodb://192.168.52.110:27017/')

    window_size = 5  # seconds

    while True:
        end_date = start_date + window_size
        dt_end = datetime.fromtimestamp(end_date)
        dt_start = datetime.fromtimestamp(start_date)
        start_date += window_size

        # Host0
        db = client['smartwatts16']
        collection = db['power']
        for target in ["node0", "node1", "node2", "node3"]:
            dump_target(target)
        # Remove all the other documents
        collection.delete_many({"timestamp": {'$lte': dt_end}})

        # Host1
        db = client['smartwatts17']
        collection = db['power']
        for target in ["node4", "node5", "node6", "node7"]:
            dump_target(target)
        # Remove all the other documents
        collection.delete_many({"timestamp": {'$lte': dt_end}})

        # Host2
        db = client['smartwatts18']
        collection = db['power']
        for target in ["node8", "node9", "node10", "node11"]:
            dump_target(target)
        # Remove all the other documents
        collection.delete_many({"timestamp": {'$lte': dt_end}})

        # Host3
        db = client['smartwatts19']
        collection = db['power']
        for target in ["node12", "node13", "node14", "node15"]:
            dump_target(target)
        # Remove all the other documents
        collection.delete_many({"timestamp": {'$lte': dt_end}})

        # Host3
        db = client['smartwatts20']
        collection = db['power']
        for target in ["node16", "node17", "node18", "node19"]:
            dump_target(target)
        # Remove all the other documents
        collection.delete_many({"timestamp": {'$lte': dt_end}})

        # Host3
        db = client['smartwatts21']
        collection = db['power']
        for target in ["node20", "node21", "node22", "node23"]:
            dump_target(target)
        # Remove all the other documents
        collection.delete_many({"timestamp": {'$lte': dt_end}})

        # Host3
        db = client['smartwatts22']
        collection = db['power']
        for target in ["node24", "node25", "node26", "node27"]:
            dump_target(target)
        # Remove all the other documents
        collection.delete_many({"timestamp": {'$lte': dt_end}})

        # Host3
        db = client['smartwatts23']
        collection = db['power']
        for target in ["node28", "node29", "node30", "node31"]:
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

