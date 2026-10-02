# Current release synchronization

The sanitized final upload remains immutable in `reference/final-upload.html`. Its SHA-256 is pinned by `RELEASE_CONTRACT.json`; the historical handoff audit is retained under `archive/prior-github-handoff/docs/`.

This release intentionally fixes interaction and engineering defects under the user's authorization. The contract pins the reference and approved normalized hash for every compiled module, with a reason for each changed module. Unexpected changes fail `npm test`. There is no blanket exemption for main.js and no replacement of the old reference with a new build.

Precomputed scientific input bytes remain frozen by file hashes. The Mutual project additionally compares its raw JSON to the imported compiled data and checks the parameters hash/content. The applications are compiled from editable source, not patched out of the reference HTML.

The maintained collection browser suite checks all scenes at three phases, real project-subpath URLs, offline entry points and repaired interactions. Scientific canvas pixels at the final phase are compared with the historical runtime. Tests of code behavior are not new experimental validation or a full solver recalculation.

The generated standalone HTML embeds project MIT and KaTeX notices. Each deploy directory includes a licenses folder. Preview manifests must match the current runtime and image hashes; rerender after any runtime change.
