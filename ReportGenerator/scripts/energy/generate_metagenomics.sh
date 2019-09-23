#!/usr/bin/env bash
cp conf/templates/energy/metagenomics/timestamping_config.ini conf/timestamping_config.ini

cp conf/templates/energy/metagenomics/report_generator_config.ini conf/report_generator_config.ini
sed -i 's/__PRINT_ENERGY_MAX__/PRINT_ENERGY_MAX/g' conf/report_generator_config.ini
sed -i 's/{PRINT_ENERGY_MAX}/false/g' conf/report_generator_config.ini
bash scripts/generate_report.sh 00:00_MG
bash scripts/generate_report.sh 01:00_MG
bash scripts/generate_report.sh 02:00_MG
bash scripts/generate_report.sh 03:00_MG

cp conf/templates/energy/metagenomics/report_generator_config.ini conf/report_generator_config.ini
sed -i 's/__PRINT_ENERGY_MAX__/PRINT_ENERGY_MAX/g' conf/report_generator_config.ini
sed -i 's/{PRINT_ENERGY_MAX}/true/g' conf/report_generator_config.ini
bash scripts/generate_report.sh 04:00_MG
bash scripts/generate_report.sh 05:00_MG
bash scripts/generate_report.sh 06:00_MG
bash scripts/generate_report.sh 07:00_MG

