from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checklist='''# R3 scoped request / implementation checklist

This is an implementation record of the user's R3 message, not a new design specification or a verbatim user attachment. Priority: current R3 instruction > R2 files for the explicitly named changes. Everything else retains R2.

## Preserve

23-page cover + S01-S22 sequence, formal S00-S21 copy, native WebGL2 renderer platform, TypeScript modules, scientific material/lighting style, mathematical/field/contact models, body panel, Chinese UI, Explore, offline HTML, HIGH/SAFE, build and screenshot tooling. No new mandatory click-by-click beats.

## Requested local changes

1. S01/S02: denser evenly spaced two-dimensional charge grids over the plate area, small margins, positive signs hovering over the visible upper surface, negative signs also visible, no plate occlusion.
2. S03/S04: one substantially larger camera motion then stable end, distinct ending angles, duration twice R2. No new beat.
3. S05: independent continuous default -> cyan region i -> amber layer j -> restore loop; modest emission, muted inactive materials, no Next blocking.
4. S06: keep fixed hinge/pivot kinematics and book-opening motion; hinge virtually invisible (0-0.03 opacity, no emission or shadow), remove hinge annotation/leader.
5. S07: 12-16 staggered particles on low/mid/high coupling paths, active-page independent time; these are path indicators, not freely travelling charge in air.
6. S10: dual interfaces -> strong upper emphasis -> strong lower emphasis -> variable upper dominance; highlight corresponding near-interface ions and labels. Bottom is stable and large. Afterwards only slight slow upper breathing; never replay EDL migration.
7. S12 -> S13: same square EH/EC/EB world and framing at the boundary; no legacy circular model, resets, field jump or camera jump. Only new-device internal emphasis afterwards.
8. S18: continuous two-window HC / CB, shared EC always physical common node, inactive electrode de-emphasis, smooth transition with stable dwell; nominal dwell 2.5 times R2, ambient, nonblocking.
9. S20: 1 -> 4 independent -> hold -> internal duplicate boundaries merge -> shared 4 hold -> 16. Only inner redundant borders move toward their common midlines; outer perimeter remains stable; crossfade rather than flash. No merge/expansion temporal overlap.
10. S22: replace old array ending only. A real 3-D mechanical gripper carries dense sensing skins on both inner surfaces and approaches an intact egg. Blue proximity area -> few warm first-contact cells -> expanding locally graded pressure response -> stop. No closed-loop, fracture safety, force-feedback or experimental-performance claim.
11. S22 skin: 8x12 to 10x16 cells per jaw, selected 10x16. Each central EC independent; fine EH shared boundary segments not duplicated around every pixel and not one permanently shorted grid. No giant-PCB appearance. Minimal user-requested copy only.
12. Every ambient loop uses separate active-scene time, stops updates when inactive, does not mutate main phase or PPT navigation, and supports a deterministic capture time.

## QA required

Actual type-check/build; real browser full presentation and controls; deterministic captures at 1920x1080 and 2560x1440; main transition quarter phases, extra dense samples for S12/S13 and S20; live full ambient cycles; HIGH/SAFE and dense-hero performance; unchanged-page R2 image regression; offline build and entry-point limitations recorded honestly.
'''
(R/'revision-spec/R3_SCOPED_REQUEST.md').write_text(checklist)
changelog='''# ProxiTouch R3 \u4fee\u6539\u8bb0\u5f55

\u672c\u8f6e\u57fa\u4e8e\u5b9e\u9645 R2 \u5b8c\u6574\u6e90\u7801\u5c40\u90e8\u4fee\u6539\u3002\u7ae0\u8282\u6570\u548c S00\u2013S21 \u6b63\u5f0f\u6807\u9898\u3001\u6b63\u6587\u4fdd\u6301\u4e0d\u53d8\u3002\u6ca1\u6709\u91cd\u505a\u6e32\u67d3\u5f15\u64ce\u6216\u89c6\u89c9\u98ce\u683c\u3002

|\u9875\u9762 / \u6a21\u5757|\u4fee\u6539|
|---|---|
|S01 / S02|\u4e0a\u3001\u4e0b\u5404 70 \u4e2a\u7535\u8377\u7b26\u53f7\uff0c10\u00d77 \u7f51\u683c\uff1b\u4e0a\u6781\u677f\u6b63\u53f7\u7ad6\u76f4\u4e8e\u53ef\u89c1\u8868\u9762\u4e0a\u65b9\uff0c\u4e0d\u88ab\u677f\u4f53\u6321\u4f4f\u3002|
|S03 / S04|\u660e\u663e\u5927\u89d2\u5ea6\u955c\u5934\u8f6c\u6362\u540e\u505c\u7a33\uff1b0.9\u21921.8 \u79d2\u30011.3\u21922.6 \u79d2\uff1b\u4e0d\u65b0\u589e\u5f3a\u5236\u70b9\u51fb\u3002|
|S05|7.2 \u79d2\u72ec\u7acb\u5faa\u73af\uff1a\u9ed8\u8ba4\u2192\u9752\u84ddi\u533a\u2192\u7425\u73c0j\u5c42\u2192\u6062\u590d\u3002|
|S06|\u4fdd\u7559 pivot\uff1b\u8f74\u4e0d\u900f\u660e\u5ea6 0.012\uff0c\u65e0\u53d1\u5149\u3001\u65e0\u9634\u5f71\uff1b\u79fb\u9664\u8f74\u6587\u5b57\u6807\u6ce8\u3002|
|S07|16 \u4e2a\u9519\u76f8\u8def\u5f84\u6307\u793a\u70b9\uff0c\u8986\u76d6\u4f4e\u4e2d\u9ad8\u5f27\u7ebf\uff0c\u5728\u9875\u9762\u505c\u7559\u671f\u95f4\u6301\u7eed\u79fb\u52a8\u3002|
|S10|4 \u79d2\u56db\u9636\u6bb5\u53cc\u754c\u9762\u5f3a\u8c03\uff0c\u6807\u6ce8\u540c\u6b65\uff1b\u540e\u7eed\u4e0a\u754c\u9762 5.8 \u79d2\u8f7b\u5fae\u547c\u5438\uff0c\u4e0b\u754c\u9762\u4e0d\u52a8\u3002|
|S12\u2192S13|\u5220\u9664\u4e3b\u6f14\u793a LegacyDevice \u4e16\u754c\uff1b\u4e24\u9875\u8fb9\u754c\u4f7f\u7528\u540c\u4e00\u65b9\u5f62\u6a21\u578b\u3001\u7535\u573a\u548c\u955c\u5934\u72b6\u6001\u3002|
|S18|\u4ec5 HC / CB \u4e24\u7a97\u53e3\uff0c\u5355\u7a97\u6807\u79f0 1 \u79d2\uff0c\u4e3a R2 \u7684 2.5 \u500d\uff1b\u4ea4\u66ff\u5f3a\u8c03\u4e0d\u5360\u7528\u4e3b\u52a8\u753b\u3002|
|S20|7.2 \u79d2\u6e05\u6670\u5b8c\u6210 1\u21924\u2192\u5185\u8fb9\u878d\u5408\u2192\u505c\u7559\u219216\uff1b\u5916\u6846\u4e0d\u4e8c\u6b21\u79fb\u52a8\u3002|
|S22|\u65b0\u589e\u53cc\u4fa7 10\u00d716 \u611f\u77e5\u76ae\u80a4\u5939\u9e21\u86cb\u5e94\u7528\u7ed3\u5c3e\u3002\u5171 320 \u4e2a\u72ec\u7acb EC\u3001692 \u6bb5\u4e0d\u91cd\u590d EH \u8fb9\u754c\u3002\u84dd\u8272\u63a5\u8fd1\u2192\u91d1\u8272\u9996\u89e6\u2192\u5c40\u90e8\u538b\u529b\u6e10\u53d8\u2192\u505c\u6b62\u3002|
|\u516c\u5171\u8ba1\u65f6|\u65b0\u589e `app/ambient.ts`\uff0c\u72ec\u7acb\u4e8e scene phase\uff1b\u79bb\u9875\u505c\u6b62\u66f4\u65b0\uff0c\u652f\u6301\u56fa\u5b9a\u622a\u56fe\u65f6\u95f4\u3002|
|\u5fae\u5c0f\u6e32\u67d3\u4fee\u6b63|HIGH \u7247\u5143\u7740\u8272\u5668\u5c06\u5df2\u6709\u5b9e\u4f8b alpha \u7eb3\u5165\u900f\u660e\u5ea6\uff0c\u4e0e SAFE \u4e00\u81f4\uff1b\u652f\u6301\u771f\u5b9e\u7684\u5b9e\u4f8b\u6de1\u5165\u6de1\u51fa\u3002\u6e32\u67d3\u5668\u4ec5\u6b64\u4e00\u884c\u4fee\u6539\u3002|

## \u89c6\u89c9\u81ea\u68c0\u4e2d\u7684\u4fee\u6b63

S04 \u8c03\u6574\u7ec8\u6b62\u89d2\u5ea6\uff0c\u907f\u514d\u540e\u4fa7\u7ed3\u6784\u88ab\u524d\u4fa7\u6a21\u578b\u906e\u6321\u3002S22 \u5bf9\u5fae\u5c0f\u50cf\u7d20\u4f53\u79ef\u7684\u8fb9\u89d2\u505a\u51e0\u4f55\u68c0\u67e5\uff0c\u6d88\u9664\u63a5\u89e6\u533a\u8fb9\u7f18\u7a7f\u5165\u9e21\u86cb\u7684\u73b0\u8c61\uff1b\u52a0\u5165\u4e0b\u65b9\u5c0f\u5b9a\u4f4d\u652f\u5ea7\uff0c\u907f\u514d\u5939\u6301\u524d\u60ac\u7a7a\uff1b\u52a0\u5f3a\u9996\u89e6\u50cf\u7d20\u7684\u6696\u91d1\u8272\u3002\u4fdd\u7559\u666e\u901a\u6750\u8d28\u4e0e\u706f\u5149\u98ce\u683c\u3002

\u96f6\u65f6\u957f\u4e3b\u52a8\u753b\u7684\u7a33\u5b9a\u7ec8\u6001\u73b0\u5728\u4e5f\u8bb0\u5165\u5b8c\u6574\u64ad\u653e\u5386\u53f2\uff0c\u4f46\u4e0d\u6539\u53d8 Next \u8bed\u4e49\u3002\u6b63\u6587\u5bfc\u5165\u811a\u672c\u4fdd\u7559 S22 \u7684 R3 \u8986\u76d6\u3002

## \u4e0d\u4f5c\u7684\u58f0\u660e

\u5939\u9e21\u86cb\u4e3a\u9884\u8bbe\u8f68\u8ff9\u4e0e\u6982\u5ff5\u54cd\u5e94\uff0c\u4e0d\u4ee3\u8868\u95ed\u73af\u63a7\u5236\u3001\u5b89\u5168\u6293\u53d6\u5df2\u9a8c\u8bc1\u3001\u4e0d\u4f1a\u5939\u7834\u3001\u529b\u53cd\u9988\u5df2\u5b9e\u6d4b\u6216\u538b\u529b\u5df2\u6807\u5b9a\u3002\u5b9e\u4f53 GPU \u548c\u6559\u5ba4\u6295\u5f71\u672a\u9a8c\u8bc1\u3002
'''
(R/'docs/CHANGELOG.md').write_text(changelog)
arch=(R/'docs/history-r2/ARCHITECTURE.md').read_text().replace('# Revision 2 architecture','# Revision 3 architecture')
arch=arch.replace('`SceneDefinition + phase -> scenePatch -> deriveState -> WorldManager -> Renderer + HUD`','`SceneDefinition + main phase + independent active-scene AmbientClock -> scenePatch / deriveState -> WorldManager -> Renderer + HUD`')
arch=arch.replace('|`models/LegacyDevice.ts`|Brief old-architecture reference in S13 only, never the final device.|','|`models/LegacyDevice.ts`|Retained unused comparison asset; no import, instance or world in the presentation WorldManager.|\n|`models/ApplicationHero.ts`|S22 only: instanced 10x16 skins per jaw, independent EC cells and unique EH edges, intact analytic egg, preprogrammed grip.|\n|`app/ambient.ts`|Separate active-scene clock and pure material/flow/breath/multiplex functions; fixed-time capture override.|')
arch=arch.replace('Exact formal copy imported from revision file 01.','Formal R2 copy S00-S21 plus the explicit S22 R3 override.')
arch+='''\n## R3 local implementation details\n\nOnly one renderer line is changed from R2: HIGH material alpha now multiplies per-instance vertex alpha, as SAFE already did. This makes array crossfade and ion de-emphasis work rather than silently discarding instance alpha. Lighting and geometry pipelines are otherwise preserved.\n\nS12 ends and S13 starts in the same deviceWorld with identical device parameters and fitted camera. S13 never instantiates LegacyDevice. The actual model viewport at this boundary is compared pixel-for-pixel and live rendered S13 node names are traced.\n\nS20 separates merge and expansion. At arrayCount=4, only the eight internal duplicate rails converge; outer rail transforms do not change. New unique rails crossfade in. There is a stable merged-4 interval before growing to 16. Scanning emphasis begins after expansion. S21 retains its R2 geometry and behavior.\n\nThe S22 jaws use real 3-D instanced cell and boundary meshes. Each skin has 160 ECs and 346 unique segmented EH boundaries, with small nonshorting junction gaps. They are explanatory geometry, not a fabricated switching network. The egg is an unchanged lathed surface. Contact-state indentation follows an analytic envelope; finite-cell corner samples keep the mesh outside that envelope. The grip stops; no feedback controller, material failure, fracture simulation or lifting action is implemented.\n\nHIGH/SAFE use the existing quality system. The new skin does not clone a complete nine-dome device 320 times. Each EC remains visible as an independent cell. Continuous response colors are pedagogical normalized fields, not measured force values.\n'''
(R/'docs/ARCHITECTURE.md').write_text(arch)
physics=(R/'docs/history-r2/PHYSICS_NOTES.md').read_text()
physics+='''\n\n## R3 scope and additional limits\n\nNo existing capacitance, representative field-state data, EDL formation model, microdome deformation model or normalized signal formula was changed. S07 moving dots indicate spatial coupling paths, not particles of free charge moving through air. S10 only reweights stable ions/interfaces and never recomputes ion migration. Slow S18 windows are an explanatory visualization of time multiplexing, not a hardware timing specification.\n\nS22 is a preprogrammed application concept. Two dense skins approach an egg located on a small staging support. Nominal approach/contact/pressure colors come from a local geometric contact proxy. It has no calibrated force law, closed-loop grip controller, fracture model, tactile hardware, measurement data or safety guarantee. The software checks that the displayed egg mesh remains unchanged and electrode vertices stay outside its analytic envelope; those checks do not validate real egg safety or material contact mechanics.\n'''
(R/'docs/PHYSICS_NOTES.md').write_text(physics)
base=json.loads((R/'docs/r3/R2_BASELINE.json').read_text())
changes=[]
for p in sorted((R/'source/src').rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(R/'source').as_posix();old=base['files'].get(rel)
 changes.append({'path':rel,'r2Sha256':old,'r3Sha256':sha(p),'status':'new' if old is None else 'unchanged' if old==sha(p) else 'modified'})
(R/'docs/r3/SOURCE_DIFF.json').write_text(json.dumps({'basis':'Actual R2 delivery extraction; see R2_BASELINE.json','runtimeFiles':changes},indent=2))
rows='\n'.join('|`'+x['path']+'`|'+x['status']+'|' for x in changes)
(R/'docs/r3/SOURCE_DIFF.md').write_text('# R2 -> R3 runtime source comparison\n\nOriginal hashes were read from the actual R2 ZIP, not inferred from screenshots. Final hashes below correspond to editable runtime files. Unrequested scene copy S00-S21 is separately asserted by content hash. The renderer has exactly one line changed for instance alpha.\n\n|Path|Status|\n|---|---|\n'+rows+'\n')
(R/'docs/MIGRATION_MAP.md').write_text('# R3 scoped map\n\nThere is no chapter migration in R3. S00-S22 retain their IDs, order and knowledge units. Only S22 replaces the old array ending with an application concept.\n\n|Request|Runtime modules|\n|---|---|\n|S01/02 charges|models/Capacitor.ts|\n|S03/04 camera|scenes/definitions.ts|\n|S05 i/j loop|models/CompositeCapacitor.ts, app/ambient.ts|\n|S06 invisible hinge / S07 flow|models/FringeField.ts, worlds/WorldManager.ts|\n|S10 interfaces|models/IonicVolume.ts, app/ambient.ts, ui/Labels.ts|\n|S12/S13 continuity|worlds/WorldManager.ts, scenes/definitions.ts|\n|S18 HC/CB loop|models/Device.ts, app/ambient.ts, ui/HUD.ts|\n|S20 merge|models/SharedArray.ts, scenes/definitions.ts|\n|S22 application|models/ApplicationHero.ts, worlds/WorldManager.ts, scenes/copy.ts, public/style.css|\n|Clock and capture|main.ts, app/state.ts, app/ambient.ts|\n\nR2 migration records are archived under docs/history-r2 and do not override R3.\n')
(R/'docs/READ_LOG.md').write_text('# R3 source inspection record\n\nThe complete R2 source was found in the existing delivered ZIP and copied, not regenerated. The R3 user message is the scoped authority. The loaded R2 specification MDs remain the background and are superseded only where R3 explicitly changes them. No new R3 attachment is claimed.\n\nInspected source: scene definitions/copy; state, timing and navigation; WebGL renderer/scene graph/geometry/camera; Capacitor, CompositeCapacitor, FringeField, IonicVolume, Device, SharedArray, LegacyDevice; WorldManager, HUD, Labels, Plots; build/offline setup; inherited models, interactions, capture and playback tests. The local module map is MIGRATION_MAP.md.\n\nInspection found usable offline compiler, Chromium/Playwright/SwiftShader, and complete editable sources. Existing field data and contact models were retained. The one necessary renderer correction is per-instance alpha in HIGH. Engineering and browser test results are recorded in QA_REPORT.md, not inferred from source.\n\nThe R2 reading log is kept under docs/history-r2 as historical evidence only.\n')
(R/'docs/SOURCE_PROVENANCE.md').write_text('# R3 provenance\n\nStarting artifact: ProxiTouch_R2_FINAL_DELIVERY.zip from the previous delivery in this conversation. This release modifies that extracted TypeScript/WebGL2 project locally. R2_BASELINE.json records source and copy hashes; SOURCE_DIFF.json identifies every runtime file as new, modified or unchanged. No external library, new visual framework, internet model asset, generated image or font asset was introduced.\n\nSource-of-truth priority: current R3 instruction for scoped edits; otherwise R2 specifications and current implementation. R3_SCOPED_REQUEST.md is a derived implementation checklist, not an original attachment. S22 copy comes from R3_COPY_OVERRIDES.json.\n\nScreenshot provenance: actual Chromium WebGL2 rendering of the complete offline HTML. Reports store its exact SHA-256. Browser-managed navigation restrictions are documented separately from offline payload rendering.\n')
print('Scope, changelog, architecture, physics and source-diff records written.')
