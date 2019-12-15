#!/usr/bin/env bash

python3 src/timestamping/signal_experiment.py start TEST0 | python3 src/mongodb/mongodb_agent.py
python3 src/timestamping/signal_test.py start TEST0 test1 | python3 src/mongodb/mongodb_agent.py
python3 src/timestamping/signal_test.py end TEST0 test1 | python3 src/mongodb/mongodb_agent.py
python3 src/timestamping/signal_experiment.py end TEST0 | python3 src/mongodb/mongodb_agent.py
