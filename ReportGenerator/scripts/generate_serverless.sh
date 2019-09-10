#!/usr/bin/env bash
cp conf/templates/scaling/streaming/report_generator_config.ini conf/report_generator_config.ini
cp conf/templates/scaling/streaming/timestamping_config.ini conf/timestamping_config.ini
bash scripts/generate_report.sh 00:00_FW
bash scripts/generate_report.sh 01:00_FW
bash scripts/generate_report.sh 02:00_FW

cp conf/templates/scaling/microbenchmarks/report_generator_config.ini conf/report_generator_config.ini
cp conf/templates/scaling/microbenchmarks/timestamping_config.ini conf/timestamping_config.ini
bash scripts/generate_report.sh 00:00_PR
bash scripts/generate_report.sh 01:00_PR
bash scripts/generate_report.sh 02:00_PR
bash scripts/generate_report.sh 03:00_PR

cp conf/templates/hybrid/report_generator_config.ini conf/report_generator_config.ini
cp conf/templates/hybrid/timestamping_config.ini conf/timestamping_config.ini
bash scripts/generate_report.sh 00:00_HYBRID
bash scripts/generate_report.sh 01:00_HYBRID
bash scripts/generate_report.sh 02:00_HYBRID
bash scripts/generate_report.sh 03:00_HYBRID
bash scripts/generate_report.sh 00:00_CONCURRENT
bash scripts/generate_report.sh 01:00_CONCURRENT
