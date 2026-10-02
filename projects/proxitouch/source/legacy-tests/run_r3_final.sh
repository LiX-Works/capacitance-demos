#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
mkdir -p ../qa/run-logs
npm run check > ../qa/run-logs/type-check.log 2>&1
npm run build > ../qa/run-logs/build.log 2>&1
node tests/r3_models.mjs > ../qa/run-logs/model-tests.log 2>&1
node scripts/export_scene_docs.mjs > ../qa/run-logs/scene-export.log 2>&1
python tests/r3_interactions.py > ../qa/run-logs/interactions.log 2>&1
python tests/r3_ambient_playback.py > ../qa/run-logs/ambient-live.log 2>&1
python tests/r3_playback.py > ../qa/run-logs/full-playback.log 2>&1
python tests/r3_extras.py > ../qa/run-logs/extras.log 2>&1
for mode in scenes transitions ambient explore; do
  for width in 1920 2560; do
    echo "$mode $width"
    PT_WIDTH=$width python tests/r3_capture.py "$mode" > "../qa/run-logs/$mode-$width.log" 2>&1
  done
done
python tests/r3_regression.py > ../qa/run-logs/regression.log 2>&1
python tests/r3_performance.py > ../qa/run-logs/performance.log 2>&1
python tests/r3_sheets.py > ../qa/run-logs/sheets.log 2>&1
echo FINAL_QA_COMPLETE
