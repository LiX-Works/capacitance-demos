# Build and scientific reproduction

The supplied HTML and dist require no server, Node, Python, registry, CDN or remote file in order to run. A desktop browser with WebGL2 and MathML support is required. Actual browser URL-navigation limitations of the execution environment are stated in QA_REPORT.md.

## Rebuild the current frozen data

Use Node 22 (the actual tested version is recorded in QA). From source:

    node scripts/setup-offline.mjs
    npm run check
    npm run build
    npm test
    npm run preview

The offline setup extracts tools/typescript-5.8.3.tgz using Node standard libraries only. An internet connection and a global TypeScript install are not required. The single HTML will be in dist/Capacitance-Lab-offline.html. The preview server binds localhost:4173 by default; PORT can be overridden.

`npm install` is another conventional dependency path when a suitable registry is available, but no successful online npm dependency installation is claimed for this execution environment. The bundled compiler is the tested offline path.

## Recompute the physics

In a Python environment containing the versions in requirements-reproduce.txt, run:

    python physics/reproduce.py

This runs the parameter trial, independent FVM, air-only finite-width 3-D BEM checkpoints, the main 2-D angle sweep and convergence tests, epsilon-scan fields, then material-detail field maps. It rewrites data/results.json and source/src/physics/data.ts. Rebuild the HTML afterward. The work runs locally and may take several minutes; it is not a browser background solver.

The scripts share physics/model.py, which reads parameters.json. Changing input parameters requires regenerating **all** numerical data and rerunning the consistency tests; editing the rendered dimensions without regenerating the physics violates the intended workflow. The selected topology, angle range and physical assumptions are explained in MODEL_DERIVATION.md.

Field-array and solve results should match to floating-point precision on a compatible numerical stack. Timing metadata can differ. Reproducibility does not mean an arbitrary change in material or geometry remains within the analytical model's domain.

## Browser QA

From source, after building:

    python tests/interactions.py
    python tests/capture_matrix.py
    MODE=transitions python tests/capture_matrix.py
    python tests/playback.py
    python tests/offline.py
    python tests/performance.py

`tests/final_queue.py` runs the main final-capture/interaction/playback sequence. Shell environment assignment syntax in the MODE example is POSIX; on Windows set the environment variable using the shell's corresponding command.

`CHROMIUM_PATH` selects a local Chromium executable. `PT_HEADLESS=0` requests a displayed browser; `PT_SOFTWARE=0` lets the browser choose its normal GPU rather than explicit SwiftShader. A local Xvfb display may be used when no physical display exists. The harness does not modify managed browser policies. Tests which load owned HTML with set_content are not silently described as successful file/HTTP URL navigation.

Do not benchmark while other render/capture processes run. The performance report uses actual RAF intervals and gl.finish; CPU submission latency is not mistaken for frame rate.
