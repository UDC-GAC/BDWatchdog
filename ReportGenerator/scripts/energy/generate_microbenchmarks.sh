#!/usr/bin/env bash
cp conf/templates/energy/microbenchmarks/timestamping_config.ini conf/timestamping_config.ini

cp conf/templates/energy/microbenchmarks/report_generator_config.ini conf/report_generator_config.ini
sed -i 's/__PRINT_ENERGY_MAX__/PRINT_ENERGY_MAX/g' conf/report_generator_config.ini
sed -i 's/{PRINT_ENERGY_MAX}/false/g' conf/report_generator_config.ini
bash scripts/generate_report.sh 00:00_EKM

cp conf/templates/energy/microbenchmarks/report_generator_config.ini conf/report_generator_config.ini
sed -i 's/__PRINT_ENERGY_MAX__/PRINT_ENERGY_MAX/g' conf/report_generator_config.ini
sed -i 's/{PRINT_ENERGY_MAX}/true/g' conf/report_generator_config.ini
bash scripts/generate_report.sh 01:00_EKM
bash scripts/generate_report.sh 02:00_EKM

exit 0

cp conf/templates/energy/microbenchmarks/report_generator_config.ini conf/report_generator_config.ini
sed -i 's/__PRINT_ENERGY_MAX__/PRINT_ENERGY_MAX/g' conf/report_generator_config.ini
sed -i 's/{PRINT_ENERGY_MAX}/false/g' conf/report_generator_config.ini
bash scripts/generate_report.sh 00:00_EPR

cp conf/templates/energy/microbenchmarks/report_generator_config.ini conf/report_generator_config.ini
sed -i 's/__PRINT_ENERGY_MAX__/PRINT_ENERGY_MAX/g' conf/report_generator_config.ini
sed -i 's/{PRINT_ENERGY_MAX}/true/g' conf/report_generator_config.ini
bash scripts/generate_report.sh 01:00_EPR
bash scripts/generate_report.sh 02:00_EPR
bash scripts/generate_report.sh 03:00_EPR


