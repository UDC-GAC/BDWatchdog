#!/usr/bin/env bash
#export RESCALER_PATH=$DEV_PATH/AutomaticRescaler
#export BDWACHDOG_PATH=$DEV_PATH/MetricsFeeder
export APPLICATION_TIMESTAMPS_PATH=$DEV_PATH/TimestampsSnitch
#export PYTHONPATH=$RESCALER_PATH:$BDWACHDOG_PATH:$APPLICATION_TIMESTAMPS_PATH

echo "Generating report for experiment $1"
mkdir -p $APPLICATION_TIMESTAMPS_PATH/pandoc_reports/$1
cd $APPLICATION_TIMESTAMPS_PATH/pandoc_reports/$1
python3 ${APPLICATION_TIMESTAMPS_PATH}/src/reporting/report_generator.py $1 > $1.txt
if [[ $? -eq 0 ]]
then
    pandoc $1.txt --latex-engine=xelatex --variable=fontsize:8pt --number-sections --toc --template $APPLICATION_TIMESTAMPS_PATH/src/reporting/simple_report.template -o $1.pdf
    if [[ $? -eq 0 ]]
    then
        echo "Successfully generated report"
    fi
    rm *.eps
fi
cd $APPLICATION_TIMESTAMPS_PATH

