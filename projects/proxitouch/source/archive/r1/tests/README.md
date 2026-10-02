# Reproducing the checks

Runtime and build do not require Python. The browser/solver tests do.
Install the versions listed in `../requirements-qa.txt` in a separate Python environment. Chromium must also be installed, either through Playwright's normal installation command or as a local browser selected by `CHROMIUM_PATH`.

Run these commands from `source/`, after building:

```sh
npm run test:numerical
python tests/capture_scenes.py ../qa/reproduced-scenes
python tests/capture_transitions.py ../qa/reproduced-transitions
python tests/explore_interaction.py
python tests/full_playback.py
python tests/performance.py
```

`final_regression.py` runs the final capture/performance/playback sequence. The full playback is unaccelerated and takes approximately 11 minutes on the tested software renderer. Its timeout is 1000 seconds. Do not run other GPU-heavy jobs while measuring performance.

The default QA path uses an isolated Chromium page populated with the complete owned HTML via `set_content`. This keeps the test independent of HTTP routing and does not change managed browser navigation policies. The delivery environment blocked all URL navigation, so normal browser HTTP/file navigation was not exercised there. The HTTP server was separately checked with actual requests.

Environment controls:

- `CHROMIUM_PATH`: installed browser executable. Without it, use system Chromium or Playwright's installed browser.
- `PT_HEADLESS=0`: visible browser window; an existing display is used by default, otherwise the harness requests headless mode.
- `PT_SOFTWARE=0`: allow the browser to select its normal graphics backend. The default QA path explicitly selects SwiftShader.
- `PT_OFFLINE_BROWSER=1`: disable network in the isolated context before the application is loaded.
- `PT_WIDTH` and `PT_HEIGHT`: viewport used by `capture_scenes.py`.
- `PT_TRANSITIONS`: comma-separated transition identifiers for a focused rerun.

On a Linux machine without a display, a local Xvfb display may be needed for the installed Chromium configuration. The delivery was tested with DISPLAY=:99. No physical GPU, Windows/macOS installation, projector or non-Chromium engine was validated by these tests.

The phase-sampling performance benchmark records real requestAnimationFrame intervals and also calls gl.finish. CPU command-submission durations are **not** presented as GPU frame rate. A high software-rendering result is not a claim about any physical GPU.

## Renderer startup note

This managed Chromium occasionally failed to create WebGL2 in headless mode. The final regression therefore used headed Chromium on the existing Xvfb display, with SwiftShader selected explicitly. The harness uses an existing X display when present; set `PT_HEADLESS=1` to request headless mode or `PT_HEADLESS=0` to request headed mode. It never changes browser policies. A startup failure is reported separately from a successful application test.
