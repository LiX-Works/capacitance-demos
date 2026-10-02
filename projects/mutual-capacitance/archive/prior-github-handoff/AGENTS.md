# Instructions for Codex / repository agents

The task for this repository is DEPLOYMENT of an existing finalized presentation, not redesign.

1. Read CODEX_DEPLOY.md, project.json and docs/SOURCE_SYNC.md first. This is one independent project; do not mix its source/data with the other archive.
2. Treat reference/final-upload.html as the privacy-sanitized authoritative user snapshot. The current source has been synchronized to its copy, animation and UI behavior. Preserve these unless the user explicitly requests another change.
3. Edit source/src, source/public and source/index.html. Do not modify only index.html, dist/app.js or a standalone HTML; those are regenerated.
4. Build with npm run build:offline, type-check with npm run check, then npm test. Root index.html, dist and site must originate from this source. Source synchronization tests intentionally fail if behavior/copy changes without an approved new reference.
5. Do not restore presenter names, supervisor names, phone numbers, student numbers, author-info blocks or personal input filenames. Keep the public first page anonymous. Third-party library copyright notices must remain.
6. Use the existing previews directory as representative real-browser renders. Do not present old screenshots as current, or generate mockups and call them browser renders.
7. Physics/solver programs and precomputed data are backup/reproduction assets. GitHub Pages runs the already-built static application; never add a server or online Python dependency just to deploy it.
8. Default deployment is .github/workflows/pages.yml, which builds and uploads ONLY site/. Preserve relative asset links and test a project-repository subpath. Do not configure a custom domain without the user asking.
9. Ask for / resolve the user's target owner, repository and visibility before creating a repository. Do not hard-code credentials, put tokens into source, force-push or rewrite unrelated history. Use existing authenticated tooling; request only genuinely missing authorization.
10. Do not execute archive/editorial-scripts or legacy-tests as current build tasks. They retain historical editing assumptions. The maintained current tests live in source/tests.
11. This is a full backup-style handoff. The zip itself is not the website: extract it, and place this directory's CONTENTS at the repository root. Do not commit node_modules, browser profiles, caches or the delivery ZIP itself.
12. Before claiming success, inspect the actual deployed URL: initial page, no personal block, representative scenes, interruptible Next, field modes where present, offline/local build and preview gallery. Report exactly what was tested versus blocked.
