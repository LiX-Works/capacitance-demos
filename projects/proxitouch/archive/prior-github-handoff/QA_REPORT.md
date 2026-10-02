# ProxiTouch - source synchronization and deployment preparation QA

## Result and authority

**The editable source, rebuilt application and deployment entries are synchronized to the user's final uploaded HTML, with the requested homepage personal information removed.** The upload is the content/behavior authority; an earlier archive is not silently substituted. This task prepared a repository for Codex to deploy. **No GitHub repository was created or published here.**

Final standalone runtime SHA-256:

`f65a3d7a00830af2e80c5d6b97e1d37cd2b2f5854b77ad99bc03a7533834dd01`

The privacy-cleaned uploaded reference is `reference/final-upload.html`, SHA-256 `7130d27380409fc5012a6614d201397b61b964d1b6c4699b8724f903f164bc33`. It is evidence, not a build input or source-editing location. Build output must come from `source/src/` and the current local assets.

## Source-level checks

The inline uploaded bundle was parsed module by module and compared against the original archive's TypeScript output before changes. The current static synchronization suite contains 35 successful checks across 29 retained runtime modules. Details and normalized module hashes are in `qa/source-sync.json`.

All 29 module identities are retained. The 28 modules outside the main controller match the cleaned upload after normalization. The upload's appended repeat-animation script is integrated into typed `source/src/main.ts`, rather than left as an output-only patch. Its next/previous, scene loading, restart, ping-pong loop and Explore behavior are exercised against the uploaded reference. Current S05/S07 wording and S05 labels are synchronized. No data table or physical solver was changed.

## Actual browser checks

- **81/81 checks passed.**
- Each of the **23/23 scene final states** was compared to the privacy-cleaned upload: model/camera state, rendered title/copy, and raw WebGL canvas PNG bytes agreed.
- Actual loop/navigation controls were exercised, including interrupting the current animation to move to the next page. The report states each check, rather than equating screenshots with functional testing.
- Preview rendering used HIGH quality. There are **12 original representative PNGs** in `previews/`, including a **2560 x 1440** capture, plus a nine-panel derived overview and a local gallery. The overview is a montage of those screenshots, not another independent render.
- Representative images were manually inspected using contact sheets and selected individual images. See `qa/manual-review.json` and `previews/manifest.json` for scope and image hashes.
- No JavaScript/console errors or external resource requests were recorded in the final browser tests. Preview extras have their own `qa/preview-extras.json` record.

The test browser was Chromium 144 using ANGLE/SwiftShader in an isolated offline context. Managed browser policy blocks URL navigation in this environment. Tests therefore load the owned complete HTML into `about:blank` with Playwright `set_content`; they do not change the policy. This is an actual browser/WebGL render but **not** a claim that normal file/HTTP browser navigation or an online Pages URL was tested here.

## Build and local deployment checks

The build was repeated from a state with no `source/node_modules`. The bundled compiler was bootstrapped without a registry download, followed by `npm run build:offline`, `npm run check`, and `npm test`. All exited successfully. Before/after runtime hashes are identical (`qa/clean-build.json`). The release ZIP excludes the installed node_modules and retains the offline compiler archive.

`index.html`, `dist/ProxiTouch-offline.html` and `site/index.html` contain the same standalone application. The normal split-asset `dist/index.html` is also regenerated. Source maps come from the updated source and use relative paths.

The Pages workflow was structurally checked and its build/test commands ran locally. The static preview server returned HTTP 200 for four actual requests: the application root, preview gallery, overview image and preview manifest. Relative links in the split entry and galleries were checked (58 checks). The workflow and online authorization/Pages settings still require execution in the user's target GitHub account.

## Privacy

Homepage author/supervisor and number information was removed from the actual DOM-generating source, CSS/visibility plumbing, and generated documents. It was not merely covered or hidden. Personal input filenames and unsanitized uploads are not in the release. New screenshots come from the sanitized build. A release scan checks known personal identifiers and their Unicode-escaped forms in code, source maps, docs and historical text. No font files are distributed; third-party copyright/license attribution is preserved.

## Historical backups and limits

`archive/`, `docs/historical/` and `source/legacy-tests/` preserve inherited materials. They may describe prior one-shot playback, old task scopes, older paths or prior numerical/performance evidence. They are labelled historical and are not counted as current tests or invoked by the deployment build. Current commands and behavior are documented at the root and in `source/tests/README.md`.

This synchronization did **not** rerun the complete scientific solver pipeline, independently validate physical models, benchmark a physical GPU, certify projector legibility, or test Safari/Firefox/mobile. Prior software-rendering performance limitations are not declared fixed. The interactive scenes retain the uploaded physics, approximations, parameters and limitations.

The two packages are independent applications. Do not replace one application's sources with the other application's latest-looking files.
