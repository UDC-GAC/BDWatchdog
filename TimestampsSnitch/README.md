# Timestamps Snitch
This subproject provides a very simple tool to manage 
experiments and tests 'start' and 'end' UNIX timestamps, 
considering that an experiment encompasses several tests.

The timestamps can be used for a variety of use cases, in particular
they have been integrated with the TimeseriesViewer and the 
ReportGenerator subprojects to handle the generation of time series plots
and reports, respectively.

## Download and install
```
git clone https://github.com/JonatanEnes/bdwatchdog
cd bdwatchdog/TimestampsSnitch/
bash install_scripts/ubuntu/install-mongodb-dependencies.sh
```
## Usage and examples

the direct way to use this module is to signal for a 'start' or an 
'end' event of either an experiment or a test. 

### Experiment handling
Experiments represent a group of several tests, thus its starting 
and ending times represent the time window while all the tests 
were executed.

:exclamation: _**If the mongodb database schema defined on this 
project is to be used, experiment names must follow the format 
"+%y-%m-%d-%H:%M\_{STRING}", e.g., "19-01-20-20:30_TeraSort" 
**_ :exclamation:


##### Signal start
* To create a new experiment timestamping info, signal the start of an experiment by running:
```
python3 src/timestamping/signal_experiment.py start 19-01-01-00:01_Test

```
* and pass the generated data to the mongodb agent that will send it to be stored in the mongodb database:
```
python3 src/mongodb/mongodb_agent.py

```
* Full 'start' command:
```
python3 src/timestamping/signal_experiment.py start 19-01-01-00:01_Test \
| python3 src/mongodb/mongodb_agent.py

```

##### Signal end

* To manually signal the end of an experiment, run the same pipeline but by signaling for the end with:
```
python3 src/timestamping/signal_experiment.py end 19-01-01-00:01_Test

```
* Full 'end' command:
```
python3 src/timestamping/signal_experiment.py end 19-01-01-00:01_Test \
| python3 src/mongodb/mongodb_agent.py

```


##### Retrieving info
To get an experiment info, a simple python script is provided.
* To get the raw info as JSON, run:
```
python3 src/timestamping/get_experiment_info.py 19-01-01-00:01_Test
```
```
{"type": "experiment", "info": {"username": "root", "start_time": 1559136727, "end_time": 1559136770, "experiment_id": "19-01-01-00:01_Test"}}
```
* You can get the same info prettyfied with:
```
python3 src/timestamping/get_experiment_info.py 19-01-01-00:01_Test \
| python -m json.tool
```
```
{
    "info": {
        "end_time": 1559136770,
        "experiment_id": "19-01-01-00:01_Test",
        "start_time": 1559136727,
        "username": "root"
    },
    "type": "experiment"
}

```
* You can also extract fields from the JSON using bash tools such as 'jq' (you may need to install it), for example to get the end time:
```
python3 src/timestamping/get_experiment_info.py 19-01-01-00:01_Test 2>/dev/null \
| jq -r '.info.end_time'
```
```
1559136770
```

* You can get all the experiments using:
```
python3 src/timestamping/get_experiment_info.py ALL
```


### Tests handling
Tests represent a single execution of any application of interest. As tests are associated to an experiment, they must be signaled in a similar way as with experiments, with a start or end parameter, but besides the experiment name an additional test_name parameter is needed.

* Full 'start' command:
```
python3 src/timestamping/signal_test.py start 19-01-01-00:01_Test Test_0 \
| python3 src/mongodb/mongodb_agent.py

```

* Full 'end' command:
```
python3 src/timestamping/signal_experiment.py end 19-01-01-00:01_Test Test_0 \
| python3 src/mongodb/mongodb_agent.py

```

* To 'delete' a test:
```
python3 src/timestamping/signal_test.py delete 19-01-01-00:01_Test Test_0
```



##### Retrieving info
To get a test info, a simple python script is provided.
* To get the raw info as JSON, run:
```
python3 src/timestamping/get_test_info.py 19-01-01-00:01_Test Test_0
```
```
{"type": "test", "info": {"username": "root", "start_time": 1559142889, "end_time": 1559143106, "experiment_id": "19-01-01-00:01_Test", "test_id": "19-01-01-00:01_Test_Test_0"}}
```
* You can get the same info prettyfied with:
```
python3 src/timestamping/get_test_info.py 19-01-01-00:01_Test Test_0\
| python -m json.tool
```
```
{
    "info": {
        "end_time": 1559143106,
        "experiment_id": "19-01-01-00:01_Test",
        "start_time": 1559142889,
        "test_id": "19-01-01-00:01_Test_Test_0",
        "username": "root"
    },
    "type": "test"
}

```
* You can also extract fields from the JSON using bash tools such as 'jq' (you may need to install it), for example to get the end time:
```
python3 src/timestamping/get_test_info.py 19-01-01-00:01_Test Test_0 2>/dev/null \
| jq -r '.info.end_time'
```
```
1559143106
```