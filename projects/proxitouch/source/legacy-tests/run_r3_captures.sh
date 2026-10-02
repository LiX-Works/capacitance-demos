#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
PT_WIDTH=2560 python tests/r3_capture.py scenes > ../qa/iterations/scenes-2560.log 2>&1
python tests/r3_capture.py transitions > ../qa/iterations/transitions-1920.log 2>&1
PT_WIDTH=2560 python tests/r3_capture.py transitions > ../qa/iterations/transitions-2560.log 2>&1
python tests/r3_capture.py ambient > ../qa/iterations/ambient-1920.log 2>&1
PT_WIDTH=2560 python tests/r3_capture.py ambient > ../qa/iterations/ambient-2560.log 2>&1
python tests/r3_capture.py explore > ../qa/iterations/explore-1920.log 2>&1
PT_WIDTH=2560 python tests/r3_capture.py explore > ../qa/iterations/explore-2560.log 2>&1
