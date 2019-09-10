#!/usr/bin/env bash
cp conf/templates/metagenomics/report_generator_config.ini conf/report_generator_config.ini
cp conf/templates/metagenomics/timestamping_config.ini conf/timestamping_config.ini
bash scripts/generate_report.sh 00:00_MG
bash scripts/generate_report.sh 01:00_MG
bash scripts/generate_report.sh 02:00_MG
bash scripts/generate_report.sh 03:00_MG

