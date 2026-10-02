# Package notes

The visible application, numerical result arrays and QA reports use the final runtime hash recorded in QA_REPORT.md. Source maps are included with normal ESM output for debugging. The standalone HTML does not fetch those source maps or the ESM tree.

The optional TypeScript archive was locally repackaged from the installed TypeScript 5.8.3 package. Compiler source contents were not changed. It includes its Apache-2.0 license and no font files. No online package installation is claimed.

To reproduce browser tests, use the maintained tests in source/tests; early development patch scripts and preview probes are deliberately excluded. The source/scenes file is the actual application copy; docs/SCENE_COPY.md is a readable export. The current uploaded specifications are preserved under spec-pack and their exact uploaded names/checksums are in docs/READ_LOG.json.

The finite-width correction is not silently applied to the main curve. The HTML presents the direct 2-D-width extrapolation and identifies the independent 3-D air checkpoints. Data/results.json contains all original SI values and the display sampling metadata, not just screenshot-ready normalized curves.
