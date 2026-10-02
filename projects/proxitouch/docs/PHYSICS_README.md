# Preserved ProxiTouch physical models and offline field generation

This synchronized delivery retains the exact physical-model modules and generated tables from the final uploaded HTML. It changes neither dimensions, material laws, conceptual assumptions nor numerical values. It is a course-level conceptual visualization, not a manufactured or experimentally calibrated device.

## Current representative field family

`source/src/models/FringeField.ts` and `source/src/models/Device.ts` consume `source/src/physics/revisionFieldData.ts`. The retained generator is:

```sh
python source/scripts/physics/solve_revision_fields.py
```

New generator runs keep elapsed runtime only in `qa/field-solver.json`, so machine-dependent timing is not embedded in new scientific tables. The frozen historical `revisionFieldData.ts` remains unchanged, including any runtime metadata inherited from its original generation.

The script is a representative two-dimensional finite-volume Laplace calculation. It uses a 145 by 111 grid, insulating outer boundaries, a fixed book-opening pivot, and a target with finite reference coupling rather than prescribing every target as a perfectly grounded conductor. It produces book-morph, approach and representative square-pixel sections. Visual depth slices extend the explanatory section into the 3-D stage; they are not a full corner-resolved 3-D device FEM solution.

Running the generator overwrites the corresponding TypeScript table and a QA report. It requires NumPy and SciPy (versions listed in `source/requirements-qa.txt`). It is not needed to build or deploy the existing application, and the full numerical generation was not rerun during this source-synchronization task.

## Historical models retained for backup

`source/scripts/physics/solve_field.py` and `solve_halo.py` correspond to the earlier section and annular-bus families retained in `fieldData.ts` and `haloFieldData.ts`. They remain as source history and possible comparison assets. They must not be used to replace the current EH/EC/EB structure simply because they are present in the repository.

## Interface, mechanics and signals

`source/src/models/IonicVolume.ts`, `CompositeCapacitor.ts`, `Dome.ts`, `Device.ts`, `SharedArray.ts`, and `ApplicationHero.ts` retain the final uploaded behavior. The ionic particles are explanatory visual elements, not molecular dynamics. Mechanical contact and displayed capacitance are teaching models with the assumptions already stated in the application. The egg-grasp scene is not evidence of a validated safe-grasp controller.

`source/src/physics/interaction.ts` supplies the shared normalized interaction state. HC and CB readout modes share the same EC physical electrode. The repository distinguishes actual numerical field data from normalized conceptual signals; synchronization tests do not upgrade either into experimental validation.

## Rebuild after an explicitly approved scientific change

Use `npm run build:offline` from the repository root. The existing `npm test` intentionally checks agreement with the approved final uploaded HTML. An intentional new model or data change requires a separate, reviewed baseline update; a deploy-only task must not alter that baseline or weaken its tests.
