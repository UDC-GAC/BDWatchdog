#!/usr/bin/env bash
bash convert_svg_to_png.sh
aws s3 cp logo.png s3://jonatan.enes.udc/bdwatchdog_website/logo_bdwatchdog.png --acl public-read
aws s3 cp icon.png s3://jonatan.enes.udc/bdwatchdog_website/icon_bdwatchdog.png --acl public-read

aws s3 cp --recursive footer/ s3://jonatan.enes.udc/bdwatchdog_website/footer/ --acl public-read

