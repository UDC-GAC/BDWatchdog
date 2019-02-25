#!/usr/bin/env bash
cat in.txt | ../../pipes/validator.py > output.txt 2> errors.log

DIFF_OUTPUT_FILES=`diff expected_output.txt output.txt`

if [ -z "$DIFF_OUTPUT_FILES" ]; then
  echo "VALIDATOR OK"
else
  echo "VALIDATOR FAIL"
fi

