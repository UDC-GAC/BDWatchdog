# Timestamps Snitch
This module provides a very simple tool to account for experiments and tests 'start' and 'end' UNIX timestamps, considering that an experiment encompasses several tests.

The timestamps can be used for the reporting utility of this module as well as with the timeseriesViewer module.

## Download and install
```
git clone https://github.com/JonatanEnes/bdwatchdog
cd TimestampsSnitch
bash install_scripts
```
## Usage and examples

the direct way to use this module is to signal for a 'start' or an 'end' evtn of either an experiment or a test. Ad additional parameter that sets the experiment name is needed.

### Experiment handling
Experiments represent a group of several tests, thus its starting and ending times represent the time window while the individual tests were executed.


* To create a new experiment timestamping info, signal the start of an experiment by running:
```
python src/timestamping/signal_experiment.py start Experiment_0

```
* and pass the generated data to the mongodb agent that will send it to be stored in the mongodb database:
```
python src/mongodb/mongodb_agent.py

```
* Full 'start' command:
```
python src/timestamping/signal_experiment.py start Experiment_0 | python src/mongodb/mongodb_agent.py

```

* To manually signal the end of an experiment, run the same pipeline but by signaling for the end with:
```
python src/timestamping/signal_experiment.py end 19-01-20-20:30_TeraSort

```
* Full 'end' command:
```
python src/timestamping/signal_experiment.py end 19-01-20-20:30_TeraSort | python src/mongodb/mongodb_agent.py

```

### Tests handling
Tests represent a single execution of any application of interest. As tests are associated to an experiment, they must be signaled in a similar way as with experiments, with a start or end parameter, but besides the experiment name an additional test_name parameter is needed.

* Full 'start' command:
```
python src/timestamping/signal_test.py start 19-01-20-20:30_TeraSort Test_0 | python src/mongodb/mongodb_agent.py

```

* Full 'end' command:
```
python src/timestamping/signal_experiment.py end 19-01-20-20:30_TeraSort Test_0 | python src/mongodb/mongodb_agent.py

```
:exclamation: _**If the mongodb database schema defined on this project is to be used, experiment names must follow the format "+%y-%m-%d-%H:%M\_{STRING}", e.g., "19-01-20-20:30_TeraSort" **_ :exclamation:


### Retrieving info
To get and experiment info, a simple python script is provided.
* To get the raw info as JSON, run:
```
python src/timestamping/get_experiment_info.py 19-01-20-20:30_TeraSort
```
```
{"type": "experiment", "info": {"username": "root", "start_time": 1550694600, "end_time": 1550702020, "experiment_id": "19-01-20-20:30_TeraSort"}}
```
* You can get the same info prettyfied with:
```
python src/timestamping/get_experiment_info.py 19-01-20-20:30_TeraSort | python -m json.tool
```
```
{
    "type": "experiment",
    "info": {
        "username": "root",
        "start_time": 1551257632,
        "end_time": 1551257639,
        "experiment_id": "19-01-20-20:30_TeraSort"
    }
}
```
* You can also extract fields from the JSON using bash tools such as 'jq', for example to get the end time:
```
python3 TimestampsSnitch/src/timestamping/get_experiment_info.py 19-01-20-20:30_TeraSort 2>/dev/null | jq -r '.info.end_time'
```
```
1551257639
```

