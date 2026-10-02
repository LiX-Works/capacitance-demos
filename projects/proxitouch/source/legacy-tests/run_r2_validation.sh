#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python tests/r2_interactions.py
python tests/r2_capture.py ../qa/captures/1920x1080
PT_WIDTH=2560 python tests/r2_capture.py ../qa/captures/2560x1440
python tests/r2_transitions.py S02 S05 S06 S08 S09 S11 S12 S13 S14 S15 S16 S17 S18 S19 S20 S21 S22
python tests/r2_explore.py device field micro nano signal exploded
PT_WIDTH=2560 python tests/r2_explore.py device field micro nano signal exploded
python tests/r2_extras.py
python tests/r2_performance.py

PT_PLAYBACK_QUALITY=high python tests/r2_playback.py
echo FINAL_VALIDATION_COMPLETE
