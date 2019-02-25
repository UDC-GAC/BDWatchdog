# applications-timestamps-snitch
This repository provides with a very simple tool to monitor Hadoop YARN applications timestamps (start) and (end) and storing them using a MongoDB databse. Additionally it can be used to repeatedly run and store experiments times, being an experiment a series of tests or applications.

## Download and install
```
git clone https://github.com/JonatanEnes/applications-timestamps-snitch
cd applications-timestamps-snitch
bash install-python-dependencies.sh
```
## Usage and examples

The easiest way of using this tools is starting the demonized yarn snitch and then using the multiple scripts to signal the start and ending of an experiment as well as to increment the experiment id. The demonized YARN snitch should poll with a configurable interval for new applications and store their timestamps accordingly.

<br>

Alternatively, an script ('run_experiment') is provided to do all the mentioned above automatically.

### Yarn snitch daemon
* To start the Yarn snitch daemon, run:
```
python yarn-snitch-daemon.py start
```
### Experiment handling
* To run a new experiment, run the script
```
bash run_experiments.sh
```
* To manually increment the experiment id, stored in the 'experiment_id.txt' file, run:
```
python scripts/increment_experiment_counter.py
```
* To manually signal the start of an experiment, run:
```
python scripts/signal-experiment.py start

```
* To manually signal the end of an experiment, run:
```
python scripts/signal-experiment.py end

```
### Retrieving info
To get and experiment info, a script is provided.
* To get the raw info as JSON, run:
```
python scripts/get_experiment_info.py experiment_2
```
```
{"username": "jonatan", "_updated": "Mon, 17 Apr 2017 15:10:52 GMT", "start_time": 1492441849, "_links": {"self": {"href": "experiments/58f4daf9685a5f05db378b03", "title": "experiment"}, "parent": {"href": "/", "title": "home"}, "collection": {"href": "experiments", "title": "experiments"}}, "end_time": 1492441851, "experiment_id": "experiment_2", "_created": "Mon, 17 Apr 2017 15:10:49 GMT", "_id": "58f4daf9685a5f05db378b03", "_etag": "63017e847b77fda580d09df90ca28a6db7cf36f2"}
```
* You can get the same info prettyfied with:
```
python scripts/get_experiment_info.py experiment_2 | python -m json.tool
```
```
{
    "_created": "Mon, 17 Apr 2017 15:10:49 GMT",
    "_etag": "63017e847b77fda580d09df90ca28a6db7cf36f2",
    "_id": "58f4daf9685a5f05db378b03",
    "_links": {
        "collection": {
            "href": "experiments",
            "title": "experiments"
        },
        "parent": {
            "href": "/",
            "title": "home"
        },
        "self": {
            "href": "experiments/58f4daf9685a5f05db378b03",
            "title": "experiment"
        }
    },
    "_updated": "Mon, 17 Apr 2017 15:10:52 GMT",
    "end_time": 1492441851,
    "experiment_id": "experiment_2",
    "start_time": 1492441849,
    "username": "jonatan"
}
```
* You can also extract fields from the JSON using bash tools such as 'jq', for example to get the end time:
```
python scripts/get_experiment_info.py experiment_2  2>/dev/null | jq -r '.end_time'
```
```
1492441851
```

