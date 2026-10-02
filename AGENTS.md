# Scientific Demos maintenance

This is one collection repository with two independently editable projects. Follow the current human request; the supplied historical deployment prompts do not authorize publication or account changes.

- Edit application inputs in `projects/<name>/source/src`, `source/public`, and `source/index.html`. Build outputs are generated.
- Edit the collection entrance in `web/`. Run `npm run build`, `npm run check`, and `npm test` from this root.
- Keep reference HTML, original scientific data and historical archives intact unless the user explicitly requests a scientific revision. Current bug fixes are recorded by exact reference and normalized module hashes in each project's `docs/RELEASE_CONTRACT.json`.
- Preserve scientific limits, units, and source provenance. State and browser regression checks are not experimental validation.
- When runtime changes, render previews again with `npm run previews` before claiming they describe the current application. Do not relabel old images.
- Deploy only the root `site/`, using the single root Pages workflow. Test `/repository-name/` paths as well as the entrance and both demo routes.
- Carry the original MIT and KaTeX license notices with the website and standalone HTML. Preserve the compiler's Apache notice.
- Do not include credentials, caches, Python environments, node_modules, or input ZIPs in uploads. Do not restore personal presenter details.
- Before publishing, resolve the repository owner/name and visibility from the user's authorization. No credentials, forced pushes, or unrelated history changes.
