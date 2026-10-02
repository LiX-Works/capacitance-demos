# Source synchronization / what changed

## Authority

The user supplied two distinct finalized standalone HTML applications. This repository represents only one of them. `reference/final-upload.html` is that application's uploaded HTML after the requested removal of the homepage personal information block and its layout/visibility plumbing. The original personal filename and unsanitized original are intentionally not distributed. The provenance file records a SHA-256 fingerprint rather than the private filename.

The final runtime was not guessed from a prior message. The inline bundle was parsed as JavaScript, module by module, and compared to the original archive's TypeScript output. The source was then updated and rebuilt. Both visual and control behavior are compared against the cleaned upload.

## Updated source

- `source/src/main.ts`: repeat playback, immediate next-page interruption, and the final field-mode order `lines -> potential -> strength` are synchronized. Specialized pages 04 and 09 remain excluded from the generic mode cycle.
- `source/src/ui/HUD.ts`: current playback/button status is preserved. The homepage author block, its visibility selector and the associated text-panel space reservation are removed.
- `source/public/style.css`: current deep-blue controls and light-blue selected field-mode style are preserved; author-only CSS is removed.

All 15 compiled modules are compared against the cleaned uploaded bundle. Scene text and scientific modules/data match the uploaded version. Original Python BEM/FVM/3-D-check sources and parameters are preserved as backup, not rerun or recalibrated in this synchronization task.

## Build chain

`source/scripts/build.mjs` compiles editable TypeScript, creates ES modules with source maps, a local bundled app, `dist/index.html`, a standalone HTML, root `index.html`, and `site/index.html`. The deployment directory copies only the entry and selected preview gallery. Source maps are generated from the updated sources, not left over from a prior version. A clean build is checked separately for deterministic output.

`npm test` validates compiled-source synchronization with the reference. It intentionally treats the reference as a content contract, so later intentional scientific/text changes require explicit new approval rather than silently changing the test to pass.

## Privacy

The author/supervisor block and phone/student identifiers were removed, not merely hidden with CSS. The current screenshot gallery is newly rendered from the cleaned build. Old screenshots were not copied into the public preview gallery. Historical text, source and packaged assets are scanned before release. Third-party copyright and licensing notices remain intact.

## Backup / historical evidence

`archive/qa-evidence` and `source/legacy-tests` preserve old evidence and development checks as backups. They may describe older playback semantics and must not override the current uploaded reference. `archive/editorial-scripts` contains old one-off writing/packaging utilities that may assume their former authoring workspace; the current build does not call them. No claim is made that all old editorial helpers are a supported current command.

## Explicit limits

No GitHub account was modified, no repository was created, and no remote site was deployed in this session. The workflow is prepared and its local build commands are tested. Final GitHub authorization, Pages settings and the live URL must be checked by Codex on the actual account. This task preserves the model and numbers; it does not provide new physical or experimental validation.
