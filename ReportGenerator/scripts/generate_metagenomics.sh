#!/usr/bin/env bash
cp conf/templates/metagenomics/report_generator_config.ini conf/report_generator_config.ini
cp conf/templates/metagenomics/timestamping_config.ini conf/timestamping_config.ini
bash scripts/generate_report.sh 19-08-24-18:57_Metagenomics
