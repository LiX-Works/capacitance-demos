#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
while ! grep -q FINAL_QA_COMPLETE ../qa/final-run.log; do sleep 3; done
python tests/r3_transition_trace.py > ../qa/run-logs/live-transitions.log 2>&1
echo ADDITIONAL_TRACE_COMPLETE
