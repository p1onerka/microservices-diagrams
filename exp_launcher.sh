#!/bin/bash

set -u

SCRIPT="./opencode_exp.sh"

PROJECT_1=""
PROJECT_2=""

echo "========================================"
echo "Experiment on $PROJECT_1"
echo "========================================"

"$SCRIPT" "$PROJECT_1"
EXIT_CODE_1=$?

echo
echo "Exp 1 return code: $EXIT_CODE_1"
echo

echo "========================================"
echo "Experiment on $PROJECT_2"
echo "========================================"

"$SCRIPT" "$PROJECT_2"
EXIT_CODE_2=$?

echo
echo "Exp 2 return code: $EXIT_CODE_2"
echo

echo "========================================"
echo "Experiments are finished"
echo "========================================"

exit 0
