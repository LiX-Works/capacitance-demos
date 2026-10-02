"""Write revision-specific delivery documentation without touching the application build."""
from pathlib import Path
import json,hashlib,re
R=Path(__file__).resolve().parents[2]
def write(name,text):
 p=R/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text.strip()+'\n',encoding='utf-8')
read=json.loads((R/'docs/READ_LOG.json').read_text())
write('docs/READ_LOG.md','# Revision 2 source reading\n\nAll eight revision Markdown files were read in full before migration. The exact inputs are in `revision-spec/`.\n\n'+ '\n'.join('- `'+x['file']+'`: '+str(x['lines'])+' lines; SHA-256 `'+x['sha256']+'`.' for x in read)+'\n\nTotal: '+str(len(read))+' files, '+str(sum(x['lines'] for x in read))+' lines. Current instruction > 01 for copy and chapters > 02 for device physics > 03 for UI > 04 for visual changes; 05 and 06 are migration/audit references.\n\nThe recovered source was inspected at `src/scenes`, `src/app`, `src/engine`, `src/models`, `src/physics`, `src/worlds`, `src/ui`, `src/main.ts`, `scripts`, and `tests`. No replacement demo was substituted.')
write('README.md','''# ProxiTouch \u7b2c\u4e8c\u8f6e\u91cd\u6784

**\u5171\u4eab\u4e2d\u592e\u7535\u6781 \u00b7 \u65f6\u5206\u590d\u7528 \u00b7 \u5171\u4eab\u8fb9\u754c\u9635\u5217**

\u672c\u7248\u662f\u5728\u4e0a\u4e00\u8f6e\u5b8c\u6574 ProxiTouch \u6e90\u7801\u4e0a\u8fc1\u79fb\u7684\u539f\u751f WebGL2 / TypeScript \u4e09\u7ef4\u79d1\u5b66\u6f14\u793a\uff0c\u4e0d\u662f\u53e6\u505a\u7684\u7b80\u5316 demo\u3002\u4e3b\u7ebf\u4e3a\u5c01\u9762 + 22 \u4e2a\u77e5\u8bc6\u5355\u5143\uff08\u57fa\u7840 11\u3001\u8bbe\u8ba1 8\u3001\u9635\u5217 3\uff09\u3002

## \u6253\u5f00\u6f14\u793a

\u7528\u652f\u6301 WebGL2 \u7684\u684c\u9762\u6d4f\u89c8\u5668\u6253\u5f00 `dist/ProxiTouch-offline.html`\u3002\u8fd9\u4e2a\u6587\u4ef6\u5305\u542b\u8fd0\u884c\u6240\u9700\u7684\u811a\u672c\u548c\u6837\u5f0f\uff0c\u65e0\u9700 npm\u3001Node \u6216\u5916\u90e8\u7f51\u7edc\u8d44\u6e90\u3002\u5b57\u4f53\u4f7f\u7528\u64cd\u4f5c\u7cfb\u7edf\u5b57\u4f53\uff0c\u672a\u9644\u5e26\u5b57\u4f53\u6587\u4ef6\u3002

\u63a8\u8350\u6f14\u793a\u5206\u8fa8\u7387\uff1a1920\u00d71080 \u6216 2560\u00d71440\u3002\u672c\u73af\u5883\u7684 Chromium \u7981\u6b62\u6587\u4ef6\u548c HTTP \u5730\u5740\u5bfc\u822a\uff1b\u4ea4\u4ed8\u5185\u5bb9\u5df2\u7ecf\u5b9e\u9645\u6d4f\u89c8\u5668\u6e32\u67d3\uff0c\u4f46\u6587\u4ef6\u76f4\u5f00\u548c HTTP \u6d4f\u89c8\u5668\u5165\u53e3\u7684\u9a8c\u8bc1\u8fb9\u754c\u8bf7\u9605\u8bfb `QA_REPORT.md`\u3002

## \u4e3b\u8981\u64cd\u4f5c

- **\u2192 / Space**\uff1a\u52a8\u753b\u64ad\u653e\u4e2d\u5148\u7acb\u5373\u5b8c\u6210\u5f53\u524d\u9875\uff1b\u518d\u6309\u4e00\u6b21\u8fdb\u5165\u4e0b\u4e00\u9875\u3002
- **\u2190**\uff1a\u8fd4\u56de\u4e0a\u4e00\u9875\u7684\u7a33\u5b9a\u7ed3\u675f\u72b6\u6001\u3002**R**\uff1a\u91cd\u64ad\u5f53\u524d\u9875\u3002
- **T**\uff1a\u5c55\u5f00 / \u6298\u53e0\u539f\u7406\u8bf4\u660e\u3002\u6b63\u6587\u9ed8\u8ba4\u663e\u793a\uff0c\u53ef\u72ec\u7acb\u6eda\u52a8\u3002
- **E**\uff1a\u8fdb\u5165\u6216\u9000\u51fa\u63a2\u7d22\u3002**Esc**\uff1a\u8fd4\u56de\u6f14\u793a\u6216\u5173\u95ed\u5f39\u5c42\u3002
- **G**\uff1a\u76ee\u5f55\u3002**P**\uff1a\u81ea\u52a8\u6f14\u793a\u3002**Home / End**\uff1a\u5c01\u9762 / \u7ed3\u5c3e\u3002

\u63a2\u7d22\u5305\u542b\u5668\u4ef6\u3001\u7535\u573a\u3001\u5fae\u7ed3\u6784\u3001EDL\u3001\u53cc\u901a\u9053\u4fe1\u53f7\u548c\u5206\u5c42\u7ed3\u6784\u516d\u79cd\u89c6\u56fe\u3002\u62d6\u52a8\u53ef\u65cb\u8f6c\uff0c\u6eda\u8f6e\u53ef\u7f29\u653e\uff0c\u6ed1\u5757\u63a7\u5236\u5171\u4eab\u4ea4\u4e92\u6df1\u5ea6\u3002\u8fd4\u56de\u65f6\u6062\u590d\u539f\u9875\u9762\u3001\u76f8\u673a\u3001\u7269\u7406\u72b6\u6001\u548c\u6b63\u6587\u6eda\u52a8\u4f4d\u7f6e\u3002

## \u7f16\u8f91\u4e0e\u79bb\u7ebf\u6784\u5efa

\u5df2\u6d4b\u8bd5\u6784\u5efa\u73af\u5883\uff1aNode.js 22\u3002\u5728\u89e3\u538b\u540e\u7684 `source` \u76ee\u5f55\u6267\u884c\uff1a

```sh
npm run setup:offline
npm run check
npm test
npm run preview
```

`setup:offline` \u4ece\u5305\u5185 `tools/typescript-5.8.3.tgz` \u63d0\u53d6\u7f16\u8bd1\u5668\uff0c\u4e0d\u8bbf\u95ee npm \u4ed3\u5e93\u3002`npm test` \u4f1a\u5148\u6784\u5efa\uff0c\u518d\u8fd0\u884c\u6a21\u578b\u4e00\u81f4\u6027\u6d4b\u8bd5\u3002`preview` \u5728\u7aef\u53e3 4173 \u63d0\u4f9b\u9759\u6001\u670d\u52a1\u3002\u4e5f\u53ef\u53ea\u6267\u884c `npm run build` \u91cd\u65b0\u8f93\u51fa `dist/`\u3002

\u6b63\u5f0f\u6587\u6848\u6765\u81ea `revision-spec/01_FINAL_SCENE_PLAN_AND_COPY.md`\uff0c\u7531 `scripts/import_revision_copy.py` \u5bfc\u5165 `src/scenes/copy.ts`\u3002\u573a\u666f\u987a\u5e8f\u3001\u65f6\u957f\u3001\u5173\u952e\u72b6\u6001\u548c\u76f8\u673a\u5728 `src/scenes/definitions.ts`\u3002\u57fa\u672c\u6d4b\u8bd5\u4e0d\u9700\u8981 Python\u3002

## \u4ea4\u4ed8\u5185\u5bb9

|\u76ee\u5f55 / \u6587\u4ef6|\u7528\u9014|
|---|---|
|`source/src/`|\u5b8c\u6574\u53ef\u7f16\u8f91 TypeScript \u6e90\u7801|
|`dist/`|\u9759\u6001\u7ad9\u70b9\u3001ES \u6a21\u5757\u3001\u5355\u6587\u4ef6\u79bb\u7ebf HTML|
|`CONTROLS.md`|\u5b8c\u6574\u64cd\u4f5c\u8bf4\u660e|
|`PRESENTATION_GUIDE.md`|23 \u9875\u6f14\u793a\u5bfc\u822a\u4e0e\u8bb2\u89e3\u63d0\u793a|
|`docs/`|\u8bfb\u53d6\u3001\u8fc1\u79fb\u3001\u7ed3\u6784\u3001\u7269\u7406\u8fb9\u754c\u4e0e\u6765\u6e90\u8bb0\u5f55|
|`qa/INDEX.html`|\u79bb\u7ebf\u622a\u56fe\u4e0e\u6d4b\u8bd5\u8bc1\u636e\u753b\u5eca|
|`QA_REPORT.md`|\u5b9e\u9645\u6d4b\u8bd5\u7ed3\u679c\u3001\u6027\u80fd\u3001\u672a\u9a8c\u8bc1\u8303\u56f4|
|`revision-spec/`|\u672c\u8f6e 8 \u4efd\u539f\u59cb MD|
|`source/archive/r1/`|\u4e0d\u53c2\u4e0e\u65b0\u7248\u8fd0\u884c\u7684\u90e8\u5206\u65e7\u7248\u8d44\u4ea7|

## \u79d1\u5b66\u8fb9\u754c

ProxiTouch \u662f\u8bfe\u7a0b\u7ea7\u6982\u5ff5\u8bbe\u8ba1\uff0c\u672a\u5236\u9020\u3001\u672a\u5b9e\u6d4b\u3002\u4ee3\u8868\u6027 Laplace \u6a21\u578b\u4e0d\u7b49\u4e8e\u5b8c\u6574\u4e09\u7ef4\u5668\u4ef6\u9a8c\u8bc1\uff1b\u79bb\u5b50\u52a8\u753b\u4e0d\u662f\u5206\u5b50\u52a8\u529b\u5b66\uff1b\u4ea4\u4e92\u6df1\u5ea6\u548c HC / CB \u4fe1\u53f7\u4e0d\u662f\u5df2\u6807\u5b9a\u6027\u80fd\u3002\u8bf7\u5c06\u8f6f\u4ef6\u6d4b\u8bd5\u3001\u622a\u56fe\u590d\u67e5\u548c\u771f\u5b9e\u786c\u4ef6\u9a8c\u8bc1\u5206\u5f00\u7406\u89e3\u3002
''')
write('CONTROLS.md','''# \u64cd\u4f5c\u8bf4\u660e / Controls

The presentation is a slide-like sequence of 23 knowledge units. A page's internal keyframes are one continuous causal animation, not compulsory click-by-click beats.

|Control|Action|
|---|---|
|Right / Space / Page Down / Next button|During animation, immediately finish this page. A second press advances to the next page and starts its animation.|
|Left / Page Up / Previous button|Previous page at its stable ending state.|
|R|Replay the current page. In Explore, reset camera and interaction depth to -0.4.|
|T / \u539f\u7406\u8bf4\u660e|Collapse or expand the default-visible body. Scroll it independently with the wheel.|
|G / \u76ee\u5f55|Open the 23-page chapter index; selecting a page starts its animation.|
|E / \u63a2\u7d22|Enter or leave Explore; preserve presentation state and body scroll.|
|Esc|Close dialogs; leave Explore when active.|
|P|Start or stop full-sequence autoplay. Stopping autoplay does not rewind the current animation.|
|Home / End|Cover / final stable scene.|
|\u5173\u4e8e|Conceptual-model limitations and keyboard guide.|

## Explore

|Control|View / action|
|---|---|
|V|Device: shared EC in the new EH-EC-EB geometry.|
|F|Field: generic mutual field in Part I; new EH-EC device field in design pages.|
|M|Microstructure: flexible EC, air gap, domes and effective contact area.|
|N|Nano / EDL: stable lower interface; upper interface follows contact state.|
|S|HC / CB normalized signals, derived from the same interaction state.|
|X|Exploded layer view; separated layers are a structural illustration, not working gaps.|
|Drag on model|Orbit camera.|
|Wheel on model|Zoom camera.|
|Depth slider|Move from far to contact to pressure. This is a normalized teaching coordinate.|
|A / \u81ea\u52a8\u4ea4\u4e92|Run or pause an 11-second smooth exploratory interaction cycle.|
|Quality selector|High, medium, or SAFE. SAFE lowers render resolution and shading cost, not scene coverage.|

Keyboard navigation ignores repeated keydown events. Arrow keys while a slider/select is focused control that native input; leaving Explore explicitly returns focus to the canvas so global navigation works again. Text scrolling does not rotate or zoom the model. Presentation mode does not depend on dragging the camera.
''')
write('docs/ARCHITECTURE.md','''# Revision 2 architecture

This project continues the delivered native WebGL2 application. It does not introduce Vite or Three.js, nor replace the 3-D core with SVG/CSS. The old native renderer, scene graph, material lighting, camera projection and local bundler remain the platform.

## Runtime flow

`SceneDefinition + phase -> scenePatch -> deriveState -> WorldManager -> Renderer + HUD`

`ModelState` is the single deterministic source for geometry, approach, mechanical closure, dome indentation, effective contact area, signal curves, highlighting, array expansion, and multiplex illustration. There is no independent random per-frame ion motion. Geometry can be restored by setting a scene and phase. Explore uses an independent shared depth override, then restores the saved presentation state.

## Modules

|Path under source/src|Role|
|---|---|
|`scenes/copy.ts`|Exact formal copy imported from revision file 01.|
|`scenes/definitions.ts`|S00-S22, chapter metadata, durations, keyframe knots and cameras.|
|`app/state.ts`|State defaults, typed patches and derived interaction.|
|`physics/interaction.ts`|Normalized contact/area/HC/CB teaching model.|
|`physics/revisionFieldData.ts`|Deterministic precomputed representative Laplace states.|
|`engine/scene.ts`, `math.ts`, `camera.ts`|Existing scene graph, linear algebra and projection/orbit rig.|
|`engine/geometry.ts`|Existing real 3-D mesh builders, plus adjustable bevel subdivision.|
|`engine/renderer.ts`|Existing WebGL2 lighting, material, instancing, transparency, shadow and crossfade pipeline; corrected instanced fade ordering and floor early return.|
|`models/FringeField.ts`|Fixed-axis book opening, numerical field slices and equivalent target.|
|`models/CompositeCapacitor.ts`|Actual area partitions containing vertical layers.|
|`models/Dome.ts`|Nine deforming microdomes, dynamic contact geometry, vertex-bent flexible films.|
|`models/Device.ts`|New square EH / shared EC / central EB and common physical readout nodes.|
|`models/LegacyDevice.ts`|Brief old-architecture reference in S13 only, never the final device.|
|`models/SharedArray.ts`|Unique boundary segments, ownership, selected EC and local response.|
|`worlds/WorldManager.ts`|Macro/Micro/Nano/device/array worlds, framing, labels and crossfades.|
|`ui/HUD.ts`|Chinese body, collapse/scroll, chapter navigation, Explore and About.|
|`ui/Labels.ts`|World-to-screen projection with safe areas and collision diagnostics.|
|`ui/Plots.ts`|Minimal SVG signal instruments only, not substitute scientific geometry.|
|`main.ts`|PPT-style navigation, state save/restore, timing, events and QA interface.|

## Geometry and readout identity

`Device.channelNodes.HC[1] === Device.channelNodes.CB[0]` is tested by object identity: the same EC scene-graph node participates in both channels. There is not a hidden independent Tx/Rx pair around a separate final Core. Four EH rails have physical corner separations. The central EB is not a full-pixel ground plane; the carrier is dielectric in the model.

The array has 16 separate local EC nodes and 40 unique edge segments at its 4x4 ending state. Twenty-four edges have two owners; selecting a pixel activates exactly four edges. Gaps at junctions keep the display from implying an all-shorted conductor grid. Routing, switches and high-impedance states are conceptual, not implemented hardware.

## Layout and offline build

The overlay uses a flex shell and a grid separating body, model and optional signal chart. The camera fits actual visible mesh envelopes to the model cell; world labels are projected and tested against reserved regions. The body uses independently scrollable MathML/text. Only labels and carefully scoped status elements use absolute positioning.

`build.mjs` compiles editable TypeScript to ES modules with source maps and bundles the same modules for a self-contained HTML. It clears stale dist output first. KaTeX is local and renders MathML; there are no CDN assets or bundled fonts. Optional field regeneration and browser QA use Python; running the delivered HTML does not.
''')
write('docs/PHYSICS_NOTES.md','''# Physics, explanatory choices and validation boundaries

The design authority is `revision-spec/02_NEW_ARCHITECTURE_AND_PHYSICS.md`; the precise page narrative is revision file 01. This document states what the implementation actually does, rather than claiming a fabricated or measured sensor.

## Established mechanisms and conceptual choices

Capacitance, fringe-field coupling, ion redistribution, EDL formation, series interface capacitances and area-mediated iontronic response are the explanatory foundations. The exact square dimensions, segmented EH pattern, EC mechanics, scan timing, numerical teaching curves, thresholds and routing are course-level design choices. No sensitivity, resolution, detection distance, pressure range, response time or superiority metric is claimed as measured.

## Classical capacitance and nonuniform materials

S01 introduces Q/U and the ideal parallel-plate relation. S02 changes gap, overlap area and dielectric in one model. S03 does not repeat those three complete experiments. S04 compares approximate area-wise parallel and field-wise series structures. S05 maps the outer sum to a horizontal region and the inner sum to its vertical layers; independent-region / weak-fringe assumptions remain visible in the formal body.

## Book opening

The upper electrode is carried on an offset dielectric spine about a fixed axis at [0,1,0]. The angle moves monotonically from 0 to -pi with no independently translating electrode track. The finite spine offset permits a nonzero initial plate gap and a coplanar final pair. This is a mechanical/visual abstraction of opening a book, not a claim that a zero-thickness leaf with finite initial separation can rotate about its literal surface edge and satisfy both endpoints without a spine. The actual pivot, angle and local electrode position are covered by numerical regression tests.

## Representative fields and the approaching target

The new tables solve a 145x111 finite-volume Laplace section. The target is represented by an equipotential coupled to a reference through a finite lumped capacitance, not by an ideal permanent ground. Reference capacitance is a chosen model parameter (0.35 of the isolated target basis self term), not a human-body measurement. The solver reports its residual in `qa/field-solver.json`.

The 3-D view repeats representative sections in separated depth slices. A central subset uses target-affected paths, while substantial peripheral electrode-to-electrode paths remain. Runtime interpolation and bounded depth-dependent path deformation support continuity; they are not a full three-dimensional field solve. Path count and brightness are not calibrated electric flux. S08's plot uses the absolute relative change of the representative coupling; its ordinate fits that signal without renormalizing its values. A nonmonotonic curve is permitted. No universal positive or negative mutual-capacitance change is implied.

The new device field is an explanatory EH-EC section wrapped onto the four square sides, with endpoints adjusted for EC position. Complete three-terminal coupling, nonuniform material properties, switching transients, readout circuitry and cross-talk are not solved.

## EDL and two interfaces

Only S09 replays the full random-distribution -> applied potential -> redistribution -> interface accumulation sequence. Ion positions are deterministic, quasi-static interpolation, not molecular dynamics or a Poisson-Nernst-Planck simulation. There are two electrode-ionogel interfaces. The body preserves the approximate series relation and the conditional case C_bottom much larger than C_top. Later interface views inherit the formed lower-interface state and show the upper effective contact state; they do not replay the full migration.

## Pressure and actual contact geometry

Interaction depth is dimensionless. External target contact with the cover precedes closure of the EC-ionogel air gap. The upper effective interface exists only after residual gap closure and positive resolved indentation. A small preload resolves the onset visually. This is not an arbitrary channel on/off switch at a distance counter.

Indentation follows a Hertz-like monotonic teaching trend, proportional to load^(2/3). Nine domes have radius 0.70 in arbitrary scene units, with a 0.96 central height and 0.91 neighboring heights. Vertices develop a flattened top and a smooth shoulder. The central radius, neighboring contact areas and summed effective area agree with the interaction model in the software tests. No global Y scaling substitutes for dome deformation.

EC and the protective film bend by vertex deformation: the central region moves down while the rim stays fixed. Yellow geometry lies at the actual contacting dome tops under the EC film. It means effective contact area, not free-floating decoration. Material transparency and the semi-transparent equivalent target intentionally expose hidden interfaces and local pressure response. Exploded layer separation is not the working air gap.

## Shared EC, timing and signals

HC reads EH-EC; CB reads EC-EB. Both use the same physical EC node. The animated measurement window highlights a temporary readout path, not three permanently assigned DC polarities. The unused node is conceptually high impedance or controlled. The visible switching is slowed for explanation; no electronic frequency is specified or validated.

HC and CB teaching signals share the same depth/contact state. HC stays nonzero after contact, and CB includes a small precontact parasitic contribution. Their overlap is intentional. The signals are normalized educational curves, not measured capacitance. Displayed channel dominance does not establish a real fusion algorithm or calibrated threshold.

## Shared boundaries and surface response

S20 removes repeated adjacent frames and exposes a unique segmented boundary grid. Each local EC remains separate. A segment can serve either neighboring pixel, but only the selected pixel's four relevant edges are highlighted. The 4x4 topology has 40 physical segments and 24 shared interior segments. It is not a permanently shorted EH sheet.

S21 maps broad proximity and localized pressure response onto actual curved 3-D pixel surfaces. The color field is a spatial teaching model, not a measured heat map. Actual multiplex hardware, row/column routing, material hysteresis, leakage, aging, parasitic coupling, thermal effects and target variability remain engineering validation work.

## What passing QA means

Type checking, mesh/state consistency, keyboard tests, screenshots and full playback validate software behavior in the recorded browser environment. They do not validate physical sensor performance. Real GPU cadence, projector contrast and other browser/OS combinations must be checked separately. Administratively blocked file/HTTP navigation is reported separately from the allowed offline-content rendering tests.
''')
rows=[('F00 + F04','S01','Capacitance and complete relation in one knowledge unit.'),('F01-F03','S02','One model, three variable conclusions.'),('F05','S03','Static trio; no repeated experiment.'),('F06 + F07','S04','Side-by-side parallel/series explanation.'),('Capacitor extension','S05','New composite material block.'),('F08','S06','Replace tilt/slide with fixed-axis book motion and matching fields.'),('F09','S07','Inherit coplanar final state.'),('F10','S08','Finite-coupling target and retained peripheral paths.'),('F11 + F21','Removed','No extra recap pages.'),('F12-F14','S09','One multi-scale EDL formation sequence.'),('F15-F17','S10','Stable two-interface model, no repeated ion migration.'),('F18-F20','S11','One pressure/contact-area explanation.'),('D00-D03','S12','One design question.'),('D04 / old Device','S13','Brief old reference then shared central electrode.'),('D05-D08','S14','New square EH-EC-EB layers; no standalone guard page.'),('D09-D11','S15','Approach with EH-EC emphasis.'),('D12','S16','Continuous touch state.'),('D13','S17','Continuous pressure state.'),('New','S18','Conceptual alternating HC/CB readout.'),('D14-D16','S19','One integrated interaction with shared-state signals.'),('D17-D18','Explore','No mainline release or Explore slide.'),('D19','S20','Shared boundary geometry and local addressing.'),('D20-D21','S21','Curved 3-D sensing surface rather than a repeated gripper sequence.'),('D22','Removed','No 64-to-1 array reverse.'),('D23','S22','Final array hero; no mechanism replay.')]
write('docs/MIGRATION_MAP.md','# Existing source -> revision 2\n\nThe original 46 scenes are not kept as the mainline. The edited 23-scene sequence follows revision file 01. Internal TypeScript identifiers such as `core` are retained where useful for reuse; they no longer denote an independent pressure sensor alongside a separate final halo Tx/Rx pair.\n\n|Old scenes / module|New|Migration|\n|---|---|---|\n'+'\n'.join('|'+ '|'.join(r)+'|' for r in rows)+'\n\nOriginal geometry/material/engine assets were reused and modified. `LegacyDevice` is deliberately limited to the brief S13 comparison, and old application/narration/tests are outside active `src/` under `source/archive/r1/`. No old F/D pages are navigable in the new presentation.')
write('docs/CHANGELOG.md','''# Revision 2 implementation and QA corrections

1. Recovered and inspected complete R1 source; preserved the native WebGL2 pipeline and offline compiler/bundler.
2. Imported all formal page titles/body from revision file 01; reduced mainline from 46 scenes to cover + 22 pages. Replaced optional presenter notes with the default audience explanation panel.
3. Rebuilt Device geometry as four square EH rails, one shared flexible EC, air gap, nine ionogel microdomes, base and central EB. Added actual shared-node identity for HC and CB windows.
4. Replaced book kinematics and field tables; used a finite-reference-coupled equivalent target. Preserved substantial direct coupling in outlying depth slices.
5. Added vertex-bent square EC/protection; retained and adapted actual dome flattening and contact-area geometry. Made S15/S16/S17 state and fitted camera boundaries continuous.
6. Added unique shared-boundary array topology, duplicate-frame fusion and local scanning; added curved surface proximity/pressure distribution.
7. Kept old renderer lighting but fixed transparent instanced fade ordering (which caused ghost array geometry) and avoided unused floor shading work. This is not a claim of a particular hardware frame rate.
8. Removed a target-visibility discontinuity that made automatic camera fitting jump during approach; kept the target present throughout that scene.
9. Fixed a real browser keyboard regression: hidden Explore slider focus swallowed subsequent navigation. Returning to presentation now focuses the canvas and restores body scrolling.
10. Visual review prompted final spacing of the classical trio, a fitted signal ordinate without changing data, controlled title line breaks, an explicit air-gap structure label and a transparent pressure target so the local surface response remains visible.
11. Corrected a test selector (`reset-view` -> actual `reset-button`). This was a QA-script error, not an application failure. Native URL navigation is blocked by administrator policy; it is separately recorded, not counted as a pass or bypassed.

See current hashed reports and the visual review log for the final evidence scope. Earlier iteration captures are retained separately and are not represented as final-build verification.
''')
# Formal page titles and implementation timing are exported from the built modules separately.
write('source/tests/README.md','''# Revision 2 verification

From `source/`, run `npm run setup:offline`, `npm run check`, then `npm test`. The model tests import the freshly generated ES modules from `../dist/js/`; they do not require a browser or network.

Browser tests use Python Playwright and a local Chromium. `requirements-qa.txt` describes the development environment. An existing system Chromium can be selected with `CHROMIUM_PATH`; otherwise Playwright's installed browser is used. `PT_SOFTWARE=1` (default) requests SwiftShader for reproducible software-rendered evidence. `PT_SOFTWARE=0` allows native GPU selection; do not compare such results as though they were the same environment. The harness can start Xvfb when a working display is absent; `PT_HEADLESS=1` explicitly chooses headless mode.

```sh
python tests/r2_interactions.py
python tests/r2_capture.py ../qa/captures/1920x1080
PT_WIDTH=2560 python tests/r2_capture.py ../qa/captures/2560x1440
python tests/r2_transitions.py S02 S05 S06 S08 S09 S11 S12 S13 S14 S15 S16 S17 S18 S19 S20 S21 S22
python tests/r2_explore.py device field micro nano signal exploded
PT_WIDTH=2560 python tests/r2_explore.py device field micro nano signal exploded
python tests/r2_extras.py
python tests/r2_performance.py
PT_PLAYBACK_QUALITY=high python tests/r2_playback.py
```

POSIX environments can use `sh tests/run_r2_validation.sh` for the sequential suite. The same Python files can be invoked individually on other platforms. Avoid running performance tests concurrently with screenshot jobs. In execution environments with a short command wrapper, launch the suite in a persistent process and poll its log; do not mistake the wrapper timeout for a browser deadlock.

The harness loads the project's self-contained document with Playwright `set_content`; this is actual Chromium/WebGL rendering, not a mocked renderer. Extras separately test network-disabled document content, native file URL navigation, HTTP responses and browser HTTP navigation. Policy-blocked navigation is status `blocked` and is never counted as a pass. Any other failed check returns a failing exit code. Every capture report includes the SHA-256 of its input HTML.

`__PT` is the intentional QA API. `goTo` and `seek` support deterministic capture; the full playback test does not seek after starting. The screenshots alone do not prove physical sensor performance or smoothness; model tests, actual interaction tests and active-animation timing are separate evidence categories.
''')
