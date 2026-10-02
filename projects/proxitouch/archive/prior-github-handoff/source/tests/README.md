# Current synchronization tests

Run npm run check and npm test from the repository root after npm run build:offline. The static suite compares compiled modules to the privacy-sanitized uploaded HTML reference, and verifies synchronized deployment entries. ProxiTouch's former appended runtime loop is integrated into its typed main class; real-browser state/pixel tests cover that integration.

Run npm run qa with Python Playwright and Pillow available. A Chromium browser must be installed; CHROMIUM_PATH can select it. The script uses a local Xvfb display when needed on Linux and renders the complete owned HTML in an isolated offline context. It never modifies browser policies. It compares final scene states to the uploaded reference, captures the selected preview images, and exercises real navigation / looping. Rendering is measured only as functional evidence, not a hardware FPS certification.

After deliberately changing the app, rebuild and inspect the actual browser. The uploaded baseline is immutable history unless the user provides a new approved revision. Do not weaken synchronization assertions to hide accidental changes.

## Curated preview regeneration

`npm run previews` from the repository root renders all 12 images in previews/manifest.json, refreshes the nine-image overview and hashes, then rebuilds site/ so the published gallery matches. Run it after browser QA when refreshing the curated gallery; the QA suite also captures its own basic selections. `python source/tests/capture_previews.py --refresh-only` only checks existing image sizes/hashes and refreshes the montage, and refuses to relabel images for a changed runtime. The gallery page uses stable filenames.
