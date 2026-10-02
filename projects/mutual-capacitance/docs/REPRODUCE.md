# Build and scientific reproduction - current synchronized repository

## Rebuild the current approved application

From the repository root with Node 22:

```sh
npm run build:offline
npm run check
npm test
npm run preview
```

The bundled compiler is installed locally by `build:offline`; no registry access is required. The maintained inputs are `source/src/`, `source/public/` and `source/index.html`. Output is `dist/`, root `index.html`, and the deployment-only `site/`. The two standalone entries match byte for byte. No Python is required to display or deploy the existing data.

## Optional numerical regeneration

The scientific programs remain in `physics/`, with `parameters.json` and the frozen `data/results.json`. Maintenance adds failure and provenance guards without recalibrating the solver or changing the frozen scientific arrays. In a Python environment containing the dependencies in root `requirements-reproduce.txt`, run from the repository root:

```sh
python physics/reproduce.py
```

The orchestrator copies `physics/` and `parameters.json` into a fresh temporary staging directory, then calls `trial_and_validate.py`, `fvm_check.py`, `bem3d_check.py`, `generate.py`, `enrich.py`, `local_maps.py`, and `check_interpolation.py`. It publishes numerical artifacts including `data/results.json`, `source/src/physics/data.ts` and fresh `qa/*.json` only after every stage and final provenance check succeeds. Any failed numerical validation check blocks generation. Parameter changes during a run block publication. Failure during ordinary publication raises an error and restores files already replaced; a process kill or power loss during publication is not guaranteed to roll back automatically. Staging starts without old QA files, so it cannot accidentally mix current parameters with archived evidence. This is optional local computation, not an online service or the deployed browser's calculation path. It was preserved and inspected during synchronization; this delivery task did not rerun the entire scientific solver pipeline.

Geometry and units are shared through `physics/model.py` and `parameters.json`. A parameter change requires regeneration and a fresh numerical audit. Do not alter the 3-D scene's dimensions independently of the model. See `MODEL_DERIVATION.md` and `NUMERICAL_REPORT.md` for inherited scientific assumptions and previous results.

The synchronization test intentionally compares the current build with the final uploaded baseline. Regeneration may change floating-point output or timing metadata. New scientific changes need explicit approval and a separately documented baseline update; do not suppress a test mismatch to make CI pass.

## Current browser QA

From the repository root after building:

```sh
npm run qa
```

This invokes `source/tests/browser_qa.py`, compares the source-built application with the sanitized final upload, and tests presentation behavior. Python dependencies for this check are in `source/requirements-qa.txt`. Chromium must be installed. The harness can use an existing Xvfb display and owned-document `set_content` when managed browser navigation is blocked. See `source/tests/README.md` and root `QA_REPORT.md` for exact coverage and limitations.

Original capture, physics-validation and performance tests remain in `source/legacy-tests/` and are historical backups, not the current deployment acceptance command. Their old playback assumptions or paths may require deliberate migration before reuse. No new hardware frame-rate or full-device physics validation is claimed by the current source-sync tests.

## Fast maintenance regression checks

After the offline TypeScript compiler is available, from the project root:

```sh
node source/tests/model-regressions.mjs
python physics/tests/test_safety.py
```

The first command checks exploration state restoration, focused-control keyboard handling, the existing three-mode cycle and pages 04/09 exceptions, remaining playback speed, diagnostic history limits, reusable dimension geometry and material-consistent chart clipping. The second uses only Python's standard library and synthetic solver dependencies/runners to check failed validation, stale or incomplete QA hashes, staged execution, failed-stage preservation, successful publication and rollback on an injected publication error. Neither test regenerates `data/results.json` or the frozen `data.ts`.

Direct stages are primarily pipeline components. `enrich.py` requires fresh `qa/finite-width-3d.json` and `qa/independent-fvm.json` with matching parameter hashes and `complete: true`; archived reports intentionally lack a newly fabricated provenance stamp. Use the staging orchestrator for complete reproduction instead of copying historical evidence into `qa/`.
