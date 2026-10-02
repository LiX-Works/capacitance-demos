"""Assemble R3 release evidence from actual frozen-browser reports; no app changes."""
from pathlib import Path
import hashlib, html, json, platform, subprocess
from PIL import Image
ROOT = Path(__file__).resolve().parents[2]
Q = ROOT / 'qa'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads((Q / p).read_text())
freeze = sha(ROOT / 'dist/ProxiTouch-offline.html')
expected = 'ed83c4f9a5a277ad5fb6046a12659b43139d6a6eef10f328a1e2a8cf6903f78b'
assert freeze == expected

# Append only images explicitly opened in this final review pass.
review = load('VISUAL_REVIEW.json')
reviewed = {e['file'] for e in review['entries']}
observations = {
 'S01':'Distributed upper plus and lower minus grid stays legible through charge and field reveal.',
 'S02':'Gap, overlap and dielectric states retain visible surface markers and safe model framing.',
 'S03':'A single clearly visible camera sweep changes structure viewing angle and reaches a stable end.',
 'S04':'Both parallel and series structures remain distinguishable at the corrected end angle.',
 'S06':'Book opening remains one-directional with no visible axle or hinge label; field follows geometry.',
 'S10':'Upper blue and lower amber interface emphasis and labels distinguish the sequence; ions do not replay migration.',
 'S12':'Late frames contain only the square shared-electrode device; no circular legacy geometry.',
 'S13':'First frame continues the same square device; labels enter after the boundary without replacing geometry.',
 'S20':'Independent internal duplicate edges converge, crossfade and hold before expansion; outer envelope remains stable.',
 'S22':'Blue proximity precedes first gold cells, then a wider local pressure gradient; intact egg and final closed hold.'
}
new = [('review/1920x1080/transitions-S01.png',observations['S01']),
       ('review/1920x1080/transitions-S02.png',observations['S02'])]
new += [(f'review/2560x1440/transitions-{s}.png',t) for s,t in observations.items()]
new += [(f'review/{r}/explore-overview.png','All six retained Explore views at two depths fit their model and text regions; signal plots remain separate.') for r in ['1920x1080','2560x1440']]
new += [('review/hero-quality.png','Both sizes in HIGH and SAFE show complete jaws, egg and localized warm response. SAFE shading is visibly simpler.'),
        ('VISUAL_WALL.png','Twelve modified-scene summaries checked for composition, palette continuity and absence of text/model collisions.'),
        ('full-playback/completed-S22.png','Actual unaccelerated HIGH playback ends at the intact-egg pressure hold with minimal copy and visible concept disclaimer.')]
for rel,obs in new:
 if rel not in reviewed:
  p=Q/rel; assert p.is_file()
  review['entries'].append({'file':rel,'sha256':sha(p),'inspection':'single full-frame browser screenshot' if rel.startswith('full-playback/') else 'contact-sheet visual inspection','observation':obs})
  reviewed.add(rel)
assert all(sha(Q/e['file']) == e['sha256'] for e in review['entries'])
(Q/'VISUAL_REVIEW.json').write_text(json.dumps(review,indent=2,ensure_ascii=False))
md = ['# R3 actual visual review log','',review['scope'],'',f'Frozen offline HTML SHA-256: `{freeze}`','',f'Explicitly opened image files: **{len(review["entries"])}**. Contact-sheet entries contain multiple reduced frames.','', '|Opened file|Inspection|Observation|','|---|---|---|']
md += [f'|[{e["file"]}]({e["file"]})|{e["inspection"]}|{e["observation"]}|' for e in review['entries']]
(Q/'VISUAL_REVIEW.md').write_text('\n'.join(md)+'\n')

# Index each actual raw image, preserving exact requested phase and ambient time.
captures=[]
for mode in ['scenes','transitions','ambient','explore']:
 for res in ['1920x1080','2560x1440']:
  r=load(f'{mode}/{res}/report.json')
  assert r['sourceSha256']==freeze and not r['errors']
  for c in r['captures']:
   assert c['passed']
   p=Q/mode/res/c['file']; im=Image.open(p)
   assert im.size == (r['width'],r['height'])
   captures.append({'file':p.relative_to(Q).as_posix(),'width':im.width,'height':im.height,
                    'sha256':sha(p),'scenePhase':c.get('phase'),'ambientSeconds':c.get('ambientSeconds'),
                    'mode':mode,'diagnosticsPassed':True})
assert len(captures)==260
(Q/'CAPTURE_INDEX.json').write_text(json.dumps({'sourceSha256':freeze,'scope':'Final raw screenshot matrix only; excludes contact sheets, iterations, regression pairs and extra evidence.','count':len(captures),'captures':captures},indent=2))

control=load('interactions/r3-report.json'); playback=load('full-playback/report.json')
models=load('r3-model-tests.json'); extras=load('extras/report.json'); perf=load('performance/report.json')
live=load('live-transitions/report.json'); ambient=load('ambient-live/report.json'); rebuild=load('rebuild/report.json'); regression=load('regression/report.json')
for d in [control,playback,models,extras,perf,live,ambient,rebuild]:
 assert d['sourceSha256']==freeze
assert all(c['passed'] for c in control['checks']+control['inherited'])
assert playback['complete'] and len(playback['visitedScenes'])==23 and len(playback['stableEnds'])==23
assert all(c['passed'] for c in live['checks']+ambient['checks'])
assert rebuild['offlineHTMLByteIdentical'] and rebuild['copyImportByteIdentical']
assert all(c['withinOneLevelSparseRasterTolerance'] for c in regression['comparisons'])
extras_pass=sum(c['status']=='passed' for c in extras['checks']); blocked=sum(c['status']=='blocked' for c in extras['checks'])
assert (extras_pass,blocked)==(19,2)
frame13=next(c for c in control['checks'] if 'actually rendered S13' in c['name'])

# Versions and renderer observed in the actual runtime.
def version(cmd):
 return subprocess.check_output(cmd,text=True).strip()
env={'node':version(['node','--version']),'npm':version(['npm','--version']),
     'chromium':version(['chromium','--version']),'python':platform.python_version(),
     'platform':platform.platform(),'renderer':load('scenes/1920x1080/report.json')['captures'][0]['diagnostic']['renderer'],
     'hardwareGPU':False,'browserEntry':'Playwright page.set_content with complete offline HTML; file/HTTP navigation blocked by administrator policy.'}
(Q/'ENVIRONMENT.json').write_text(json.dumps(env,indent=2))
summary={'release':'ProxiTouch R3','sourceSha256':freeze,'sceneCount':23,'copyUnchangedS00ThroughS21':True,
 'modelTests':38,'interactionTests':len(control['inherited'])+len(control['checks']),
 'liveAmbientLoops':4,'fullPlaybackSeconds':playback['elapsedSeconds'],'fullPlaybackScenes':23,
 'rawMatrixScreenshots':260,'explicitVisualReviewFiles':len(review['entries']),
 'liveS13Frames':len(frame13['detail']),'liveS20Frames':live['checks'][0]['detail']['actuallyRenderedFrames'],
 'liveS22Frames':live['checks'][1]['detail']['actuallyRenderedFrames'],
 'extraChecksPassed':19,'extraChecksPolicyBlocked':2,'cleanRebuildIdentical':True,
 'fluencyAccepted':False,'hardwareGPUTested':False,'experimentalDeviceValidated':False}
(Q/'RELEASE_SUMMARY.json').write_text(json.dumps(summary,indent=2))

# Chinese QA report. Escapes keep the authoring shell entirely ASCII.
perf_rows='\n'.join(f'|{m["scene"]}|{m["quality"].upper()}|{m["averageFPS"]:.2f}|{m["activeIntervals"]}|{m["medianFrameMs"]:.1f}|' for m in perf['measurements'])
qa=f'''# ProxiTouch R3 \u6700\u7ec8\u7cbe\u4fee\uff5cQA \u62a5\u544a

## \u7ed3\u8bba\u4e0e\u8303\u56f4

\u672c\u8f6e\u57fa\u4e8e\u5b8c\u6574 R2 \u5de5\u7a0b\u505a\u5c40\u90e8\u4fee\u6539\uff0c\u4ecd\u4e3a\u5c01\u9762 + 22 \u4e2a\u77e5\u8bc6\u5355\u5143\u3002S00\u2013S21 \u6807\u9898\u4e0e\u6b63\u6587\u4fdd\u6301 R2\uff1b\u4ec5 S22 \u4f7f\u7528\u672c\u8f6e\u6307\u5b9a\u7684\u5939\u9e21\u86cb\u5e94\u7528\u6982\u5ff5\u6587\u6848\u3002\u6ca1\u6709\u66ff\u6362\u7ae0\u8282\u3001\u6e32\u67d3\u5f15\u64ce\u3001\u63a2\u7d22\u6a21\u5f0f\u6216\u89c6\u89c9\u98ce\u683c\u3002

**\u529f\u80fd\u3001\u6784\u5efa\u548c\u6307\u5b9a\u89c6\u89c9\u68c0\u67e5\u5df2\u5b8c\u6210\uff1b\u8f6f\u4ef6\u6e32\u67d3\u73af\u5883\u4e0b\u7684\u6d41\u7545\u5ea6\u9a8c\u6536\u672a\u901a\u8fc7\u3002** \u5b9e\u4f53 GPU\u3001\u8bfe\u5802\u6295\u5f71\u3001\u7528\u6237\u673a\u5668\u7684\u6587\u4ef6\u76f4\u5f00\u548c\u771f\u5b9e\u5668\u4ef6\u6027\u80fd\u672a\u9a8c\u8bc1\u3002

\u6240\u6709\u6700\u7ec8\u6d4b\u8bd5\u5bf9\u5e94\u540c\u4e00\u51bb\u7ed3\u7248\u672c\uff1a

`{freeze}`

\u8fd9\u662f `dist/ProxiTouch-offline.html` \u7684 SHA-256\uff0c\u5404 JSON \u62a5\u544a\u4e2d\u7684 `sourceSha256` \u4e0e\u4e4b\u4e00\u81f4\u3002\u622a\u56fe\u6765\u81ea\u5b9e\u9645 Chromium / WebGL2\uff0c\u4e0d\u662f\u8bbe\u8ba1\u7a3f\u3002

## 1. \u6307\u5b9a\u4fee\u6539\u7684\u9a8c\u8bc1

|\u9875\u9762|\u5b9e\u73b0\u4e0e\u68c0\u67e5|
|---|---|
|S01 / S02|\u6bcf\u5757\u6781\u677f 10\u00d77 = 70 \u4e2a\u7535\u8377\u7b26\u53f7\uff0c\u7559\u8fb9\u5747\u5300\u5206\u5e03\u3002\u4e0a\u677f\u6b63\u53f7\u6d6e\u4e8e\u53ef\u89c1\u8868\u9762\uff0c\u4e0d\u88ab\u81ea\u8eab\u677f\u4f53\u906e\u6321\u3002|
|S03 / S04|\u5355\u6bb5\u5927\u5e45\u955c\u5934\u65cb\u8f6c\u540e\u505c\u4f4f\u3002\u65f6\u957f\u5206\u522b 0.9\u21921.8 s\u30011.3\u21922.6 s\uff0c\u65f6\u95f4\u500d\u589e\uff0c\u672a\u589e\u52a0\u70b9\u51fb\u8282\u70b9\u3002|
|S05|7.2 s \u6750\u6599\u5faa\u73af\uff1a\u9ed8\u8ba4\u2192\u9752\u84ddi\u533a\u2192\u7425\u73c0j\u5c42\u2192\u6062\u590d\u3002\u4e3b\u52a8\u753b\u65f6\u957f\u4e3a\u96f6\uff0c\u4e0d\u963b\u585e\u7ffb\u9875\u3002|
|S06|\u56fa\u5b9a pivot \u4e0e 180\u00b0 \u7ffb\u4e66\u903b\u8f91\u4fdd\u7559\u3002\u8f6c\u8f74 opacity 0.012\u3001\u65e0 emission\u3001\u65e0\u6295\u5f71\uff0c\u8f6c\u8f74\u6587\u5b57\u548c\u5f15\u7ebf\u79fb\u9664\u3002|
|S07|16 \u4e2a\u9519\u76f8\u6307\u793a\u7c92\u5b50\u8986\u76d6\u4f4e\u3001\u4e2d\u3001\u9ad8\u5f27\u7ebf\uff0c\u4f7f\u7528\u72ec\u7acb ambient time\u3002\u4ec5\u8868\u793a\u8026\u5408\u8def\u5f84\uff0c\u4e0d\u4ee3\u8868\u771f\u5b9e\u7535\u8377\u7a7f\u8fc7\u7a7a\u6c14\u3002|
|S10|\u53cc\u754c\u9762\u2192\u5f3a\u8c03\u4e0a\u90e8\u2192\u5f3a\u8c03\u4e0b\u90e8\u2192\u4e0a\u90e8\u4e3b\u5bfc\uff1b\u7ed3\u675f\u540e\u4ec5\u4e0a\u754c\u9762\u8f7b\u5fae\u547c\u5438\uff0c\u4e0b\u754c\u9762\u7a33\u5b9a\uff0c\u672a\u91cd\u64ad\u79bb\u5b50\u8fc1\u79fb\u3002|
|S12\u2192S13|S13 \u4ece phase=0 \u4ec5\u4f7f\u7528\u65b0\u65b9\u5f62 deviceWorld\u3002\u5b9e\u6d4b\u8fb9\u754c\u6a21\u578b\u533a\u57df\u50cf\u7d20\u5b8c\u5168\u4e00\u81f4\uff1bS13 \u5b9e\u64ad {len(frame13['detail'])} \u5e27\u5747\u65e0 LegacyDevice\u3002|
|S18|\u4ec5 HC\u3001CB \u4e24\u4e2a\u7a97\u53e3\uff0c2 s \u4e00\u5faa\u73af\uff0c\u6bcf\u7a97\u53e3 1 s = R2 \u7684 2.5 \u500d\uff0c\u542b\u5e73\u6ed1\u8fc7\u6e21\u4e0e\u7a33\u5b9a\u505c\u7559\u3002|
|S20|1\u21924\u2192\u505c\u7559\u2192\u5185\u90e8\u91cd\u590d\u8fb9\u878d\u5408\u2192\u7a33\u5b9a4\u219216\u3002\u5b9e\u64ad 93 \u5e27\uff0c\u5176\u4e2d 24 \u5e27\u878d\u5408\u300110 \u5e27\u7a33\u5b9a4\uff1b\u878d\u5408\u671f\u5916\u8fb9\u6846\u77e9\u9635\u504f\u5dee\u4e3a 0\u3002|
|S22|\u53cc\u4fa7\u5939\u722a\uff0c\u6bcf\u4fa7 10\u00d716 \u72ec\u7acb EC \u4e0e 346 \u4e2a\u552f\u4e00\u5171\u4eab EH \u77ed\u8fb9\u3002\u84dd\u8272\u63a5\u8fd1\u2192\u5c11\u91cf\u91d1\u8272\u9996\u89e6\u2192\u5c40\u90e8\u538b\u529b\u68af\u5ea6\uff0c\u7ed3\u675f\u540e\u5939\u722a\u505c\u6b62\u3002\u5b9e\u64ad 59 \u5e27\u8986\u76d6\u4e09\u9636\u6bb5\u3002|

\u8bc1\u636e\uff1a[\u6a21\u578b\u6d4b\u8bd5](qa/r3-model-tests.json)\u3001[\u4ea4\u4e92\u6d4b\u8bd5](qa/interactions/r3-report.json)\u3001[\u5b9e\u64ad\u8f6c\u573a\u8f68\u8ff9](qa/live-transitions/report.json)\u3001[\u771f\u5b9e\u65f6\u95f4\u5faa\u73af](qa/ambient-live/report.json)\u3002

## 2. \u6267\u884c\u7ed3\u679c

|\u9879\u76ee|\u5b9e\u9645\u7ed3\u679c|
|---|---|
|TypeScript / \u6a21\u578b\u4e00\u81f4\u6027|\u7c7b\u578b\u68c0\u67e5\u901a\u8fc7\uff1b38/38\uff08R2 15 + R3 23\uff09\u901a\u8fc7|
|\u952e\u76d8\u3001\u6309\u94ae\u3001\u72b6\u6001\u6062\u590d|59/59\uff08R2 32 + R3 27\uff09\u901a\u8fc7|
|\u56db\u4e2a ambient \u5b9e\u65f6\u5faa\u73af|4/4 \u901a\u8fc7\uff1b\u4e3b\u52a8\u753b\u7ed3\u675f\u540e\u7ee7\u7eed\uff0c\u79bb\u9875\u505c\u6b62\uff0c\u4e0d\u963b\u585e Next|
|\u5b8c\u6574\u64ad\u653e|HIGH\uff0c\u672a\u52a0\u901f S00\u2192S22\uff1b23/23 \u9875\u548c 23/23 \u7a33\u5b9a\u7ec8\u6001\uff1b{playback['elapsedSeconds']:.2f} s|
|\u6700\u7ec8\u53cc\u5206\u8fa8\u7387\u622a\u56fe|260 \u5f20\uff1b\u5e03\u5c40\u3001\u516c\u5f0f\u3001\u6807\u7b7e\u3001WebGL \u8bca\u65ad\u901a\u8fc7|
|\u989d\u5916\u68c0\u67e5|21 \u9879\uff1a19 \u901a\u8fc7\uff0c2 \u9879\u5165\u53e3\u5bfc\u822a\u88ab\u7ba1\u7406\u5458\u7b56\u7565\u963b\u6b62|
|\u79bb\u7ebf\u91cd\u5efa|\u4ece\u65e0 node_modules \u72b6\u6001\u4f7f\u7528\u5305\u5185\u7f16\u8bd1\u5668\u91cd\u5efa\uff1bHTML \u9010\u5b57\u8282\u4e00\u81f4\uff1b\u518d\u5bfc\u5165\u6b63\u6587\u4e5f\u4fdd\u6301\u4e00\u81f4|

\u6240\u6709\u6700\u7ec8\u6d4b\u8bd5\u8def\u5f84\u5747\u672a\u8bb0\u5f55\u5230 JavaScript / WebGL \u9519\u8bef\u3002\u8fd9\u4e0d\u4ee3\u8868\u6240\u6709\u672a\u6d4b\u6d4f\u89c8\u5668\u548c\u786c\u4ef6\u4e0a\u90fd\u4e0d\u4f1a\u51fa\u73b0\u95ee\u9898\u3002

\u8bc1\u636e\uff1a[\u5b8c\u6574\u64ad\u653e](qa/full-playback/report.json)\u3001[\u989d\u5916\u68c0\u67e5](qa/extras/report.json)\u3001[\u5e72\u51c0\u91cd\u5efa](qa/rebuild/report.json)\u3002

## 3. \u622a\u56fe\u4e0e\u5b9e\u9645\u770b\u56fe\u8303\u56f4

|\u7c7b\u522b|1920\u00d71080|2560\u00d71440|\u5408\u8ba1|
|---|---:|---:|---:|
|\u5168\u90e8\u9875\u9762\u7a33\u5b9a\u72b6\u6001|23|23|46|
|\u5173\u952e\u8f6c\u573a\u4e2d\u95f4\u5e27|71|71|142|
|\u56db\u4e2a\u5faa\u73af\u7684\u56fa\u5b9a\u65f6\u95f4\u72b6\u6001|24|24|48|
|Explore\uff0c6 \u89c6\u56fe\u00d72 \u6df1\u5ea6|12|12|24|
|\u5408\u8ba1|130|130|260|

\u8f6c\u573a\u4e0d\u4ec5\u622a\u53d6\u8d77\u7ec8\u70b9\uff1a\u5305\u542b 0/25/50/75/100%\uff0c\u5e76\u5bf9 S12\u2192S13\u3001S20 \u878d\u5408\u4e0e S22 \u9996\u89e6\u65f6\u523b\u52a0\u5bc6\u91c7\u6837\u3002\u622a\u56fe\u6a21\u5f0f\u663e\u5f0f\u56fa\u5b9a ambient time\uff0c\u56db\u4e2a\u5faa\u73af\u7684\u91cd\u590d\u622a\u56fe\u50cf\u7d20\u4e00\u81f4\u6d4b\u8bd5\u901a\u8fc7\u3002

\u6700\u7ec8\u5b9e\u9645\u6253\u5f00\u68c0\u67e5\u7684\u56fe\u50cf\u6587\u4ef6\u4e3a **{len(review['entries'])} \u4e2a**\uff0c\u5305\u542b\u53cc\u5206\u8fa8\u7387\u7684\u5168\u9875\u8054\u7cfb\u8868\u3001\u5173\u952e\u8f6c\u573a\u8054\u7cfb\u8868\u3001\u5faa\u73af\u3001Explore\u3001\u5c40\u90e8\u653e\u5927\u548c\u5355\u5f20\u622a\u56fe\u3002**\u8054\u7cfb\u8868\u662f\u7f29\u5c0f\u590d\u67e5\uff0c\u4e0d\u662f 260 \u5f20\u9010\u5f20\u3001\u9010\u50cf\u7d20\u7684\u4eba\u5de5\u9a8c\u6536\u58f0\u660e\u3002** \u5b9e\u64ad\u8f68\u8ff9\u68c0\u67e5\u4e5f\u4e0d\u7b49\u4e8e\u6bcf\u4e2a\u65f6\u523b\u90fd\u4fdd\u7559\u4e86\u539f\u59cb\u50cf\u7d20\u5f55\u50cf\u3002

[\u5b9e\u9645\u770b\u56fe\u8bb0\u5f55](qa/VISUAL_REVIEW.md)\uff5c[\u539f\u56fe\u6e05\u5355\u4e0e\u54c8\u5e0c](qa/CAPTURE_INDEX.json)\uff5c[\u79bb\u7ebf\u753b\u5eca](qa/INDEX.html)

## 4. \u4e0d\u7834\u574f R2 \u7684\u56de\u5f52\u68c0\u67e5

\u6b63\u6587\u54c8\u5e0c\u68c0\u67e5\u786e\u8ba4 S00\u2013S21 \u672a\u6539\u300214 \u4e2a\u9501\u5b9a\u57fa\u7840\u6a21\u5757\u4e0e R2 \u5b57\u8282\u4e00\u81f4\u3002\u6e32\u67d3\u5668\u4ec5\u4fee\u6b63 HIGH \u5b9e\u4f8b alpha \u76f8\u4e58\u4e00\u884c\uff0c\u4f7f\u5176\u4e0e SAFE \u4e00\u81f4\uff0c\u7528\u4e8e\u6b63\u786e\u6de1\u5165\u6de1\u51fa\u3002

\u5b9e\u9645\u52a0\u8f7d R2 \u4e0e R3 \u79bb\u7ebf\u4ea7\u7269\uff0c\u5bf9 S00\u3001S08\u3001S09\u3001S11\u3001S14\u2013S17\u3001S19\u3001S21 \u5171 **19 \u5bf9**\u56fe\u50cf\u6bd4\u8f83\uff1a9 \u5bf9\u50cf\u7d20\u5b8c\u5168\u4e00\u81f4\uff1b\u5176\u4f5910 \u5bf9\u4ec5 1\u20133 \u4e2a\u50cf\u7d20\u53d1\u751f\u6700\u5927 1/255 \u901a\u9053\u7ea7\u5dee\u5f02\u3002\u4e0d\u5c06\u5176\u5199\u6210\u5168\u90e8\u4e25\u683c\u50cf\u7d20\u76f8\u540c\u3002S21 \u4e2d\u95f4\u548c\u7ec8\u6001\u56fe\u50cf\u5747\u5b8c\u5168\u4e00\u81f4\u3002

\u8bc1\u636e\uff1a[\u56de\u5f52\u539f\u59cb\u7ed3\u679c](qa/regression/report.json)\u3001[\u6e90\u7801\u5dee\u5f02](docs/r3/SOURCE_DIFF.md)\u3002

## 5. \u73af\u5883\u3001\u5165\u53e3\u548c\u6027\u80fd\u8fb9\u754c

- Node {env['node']} / npm {env['npm']} / \u672c\u5730 TypeScript 5.8.3\u3002
- {env['chromium']}\u3002
- WebGL2\uff1a`{env['renderer']}`\u3002

\u672c\u73af\u5883\u7684\u7ba1\u7406\u5458\u7b56\u7565\u963b\u6b62 `file://` \u548c HTTP \u6d4f\u89c8\u5668\u5730\u5740\u5bfc\u822a\u3002\u4e24\u8005\u5747\u5b9e\u9645\u5c1d\u8bd5\uff0c\u8fd4\u56de `ERR_BLOCKED_BY_ADMINISTRATOR`\uff0c\u672a\u4fee\u6539\u6216\u7ed5\u8fc7\u7b56\u7565\u3002\u6e32\u67d3\u6d4b\u8bd5\u4f7f\u7528 Playwright \u5c06\u5b8c\u6574\u79bb\u7ebf HTML \u52a0\u8f7d\u5230 `about:blank`\u3002\u65ad\u7f51\u540e\u8fd0\u884c\u901a\u8fc7\uff0c\u65e0\u7f51\u7edc\u8bf7\u6c42\uff1bHTTP \u9759\u6001\u670d\u52a1\u516d\u4e2a\u8def\u5f84\u8fd4\u56de 200\u3002\u8fd9\u4e0d\u80fd\u66ff\u4ee3\u7528\u6237\u673a\u5668\u6587\u4ef6\u76f4\u5f00\u6216 HTTP \u6d4f\u89c8\u5668\u5165\u53e3\u9a8c\u8bc1\u3002

### \u6d3b\u8dc3\u52a8\u753b FPS\uff08\u8f6f\u4ef6\u6e32\u67d3\uff09

1920\u00d71080 \u7a97\u53e3\uff1b\u9884\u70ed 1 s\uff0c\u6bcf\u9879\u81f3\u5c11\u91c7\u6837 4.5 s\uff0c\u4f7f\u7528\u5b9e\u9645 RAF \u95f4\u9694\u3002\u6027\u80fd\u6d4b\u8bd5\u65f6\u6ca1\u6709\u5e76\u884c\u6d4f\u89c8\u5668\u6d4b\u8bd5\u6216\u622a\u56fe\u7f16\u7801\u3002S21/S22 \u4f7f\u7528\u539f\u52a8\u753b\u8def\u5f84\u7684\u65f6\u95f4\u62c9\u957f\u6bb5\u4fdd\u6301\u6d3b\u8dc3\u91c7\u6837\uff1bS07/S18 \u5faa\u73af\u6309\u771f\u5b9e\u901f\u5ea6\u3002\u8fd9\u4e0e\u4e0a\u8ff0\u672a\u52a0\u901f\u5b8c\u6574\u64ad\u653e\u662f\u72ec\u7acb\u6d4b\u8bd5\u3002

|Scene|\u6863\u4f4d|\u5e73\u5747 FPS|\u91c7\u6837\u95f4\u9694\u6570|\u4e2d\u4f4d\u5e27\u95f4\u9694 ms|
|---|---|---:|---:|---:|
{perf_rows}

**\u8fd9\u4e9b\u6570\u503c\u4e0d\u6ee1\u8db3\u6d41\u7545\u6f14\u793a\u76ee\u6807\u3002** HIGH \u7684\u77ed\u91c7\u6837\u95f4\u9694\u6570\u5c11\uff0c\u53ea\u80fd\u89c6\u4e3a\u5f53\u524d\u8f6f\u4ef6\u73af\u5883\u7684\u6d4b\u91cf\uff0c\u4e0d\u5e94\u63a8\u7b97\u5b9e\u4f53 GPU \u5e27\u7387\u3002SAFE \u4f7f\u7528\u8f83\u4f4e\u5185\u90e8\u6e32\u67d3\u5206\u8fa8\u7387\u548c\u7b80\u5316\u7740\u8272\u3002\u9ad8\u5bc6\u5ea6\u5939\u722a\u4f7f\u7528\u5b9e\u4f8b\u5316\u51e0\u4f55\u800c\u975e\u590d\u5236\u6574\u5957\u5fae\u7a79\u9876\uff0c\u4f46\u5e76\u4e0d\u610f\u5473\u7740\u6027\u80fd\u5df2\u7ecf\u5168\u9762\u9a8c\u6536\u3002

\u8bc1\u636e\uff1a[\u73af\u5883](qa/ENVIRONMENT.json)\u3001[\u6027\u80fd\u539f\u59cb\u95f4\u9694](qa/performance/report.json)\u3002

## 6. \u79d1\u5b66\u4e0e\u5e94\u7528\u8fb9\u754c

\u5939\u9e21\u86cb\u662f\u9884\u8bbe\u52a8\u4f5c\u7684\u5e94\u7528\u6982\u5ff5\u6f14\u793a\uff0c\u4e0d\u662f\u81ea\u52a8\u95ed\u73af\u63a7\u5236\u3002\u9e21\u86cb\u4fdd\u6301\u5b8c\u6574\u662f\u53ef\u89c6\u5316\u72b6\u6001\uff0c\u4e0d\u662f\u4e0d\u4f1a\u5939\u788e\u7684\u5b9e\u9a8c\u8bc1\u660e\u3002\u5b9e\u73b0\u4e86\u89e6\u70b9\u6821\u51c6\u7684\u51e0\u4f55\u5305\u7edc\u68c0\u67e5\uff0c\u4f46\u672a\u8ba1\u7b97\u86cb\u58f3\u7834\u574f\u3001\u63a5\u89e6\u529b\u6216\u5b9e\u9645\u538b\u529b\u5355\u4f4d\u3002\u9635\u5217\u84dd/\u91d1\u8272\u662f\u5f52\u4e00\u5316\u8bf4\u660e\u6027\u54cd\u5e94\uff0c\u4e0d\u662f\u5b9e\u6d4b\u70ed\u56fe\u3002

\u7535\u573a\u4ecd\u4e3a\u4ee3\u8868\u6027\u573a\u6570\u636e\u4e0e\u63d2\u503c\uff1b\u79bb\u5b50\u52a8\u753b\u4e0d\u662f\u5206\u5b50\u52a8\u529b\u5b66\u3002\u5171\u4eab\u8fb9\u6846\u7684\u51e0\u4f55\u72ec\u7acb\u6bb5\u4e0e\u5c40\u90e8\u5f3a\u8c03\u4e0d\u7b49\u4e8e\u5df2\u5b9e\u73b0\u771f\u5b9e\u626b\u63cf\u7535\u8def\u3002\u672a\u5236\u9020\u3001\u672a\u5b9e\u6d4b\u5668\u4ef6\uff0c\u4e0d\u505a\u7075\u654f\u5ea6\u3001\u7ebf\u6027\u3001\u529b\u53cd\u9988\u6216\u5bff\u547d\u6027\u80fd\u58f0\u660e\u3002

## 7. \u72b6\u6001\u533a\u5206

|\u72b6\u6001|\u8303\u56f4|
|---|---|
|Implemented|\u672c\u8f6e\u6307\u5b9a\u9875\u9762\u4fee\u6539\u3001\u56db\u4e2a\u72ec\u7acb\u5faa\u73af\u3001\u65b0 S22\u3001\u6e90\u7801\u4e0e\u79bb\u7ebf\u4ea7\u7269|
|Browser tested|\u672c\u73af\u5883 Chromium \u4e2d\u7684\u5b8c\u6574\u64ad\u653e\u3001\u5b9e\u65f6\u5faa\u73af\u3001\u64cd\u4f5c\u3001Explore\u3001\u8c03\u6574\u5927\u5c0f\u3001HIGH/SAFE|
|Screenshot verified|\u5b9e\u9645\u770b\u56fe\u8bb0\u5f55\u4e2d\u7684\u9875\u9762\u3001\u8054\u7cfb\u8868\u548c\u5c40\u90e8\u590d\u67e5\uff1b\u975e\u5168\u90e8\u539f\u56fe\u9010\u50cf\u7d20\u9a8c\u6536|
|Software validated|\u5217\u51fa\u7684\u6d4b\u8bd5\u7528\u4f8b\u3001\u786e\u5b9a\u6027\u622a\u56fe\u3001\u8fb9\u754c\u4e00\u81f4\u6027\u3001\u79bb\u7ebf\u91cd\u5efa\uff1b\u4e0d\u4ee3\u8868\u6574\u4e2a\u9879\u76ee\u5168\u9762\u9a8c\u8bc1|
|Unverified|\u5b9e\u4f53 GPU\u3001\u8bfe\u5802\u6295\u5f71\u3001\u5176\u4ed6\u6d4f\u89c8\u5668/\u7cfb\u7edf\u3001\u771f\u5b9e\u7535\u8def\u548c\u5b9e\u9a8c\u6027\u80fd|
|Not accepted|SwiftShader \u6d41\u7545\u5ea6\uff1b\u53d7\u7b56\u7565\u9650\u5236\u7684\u6587\u4ef6/HTTP \u6d4f\u89c8\u5668\u5165\u53e3\u672a\u5b8c\u6210\u9a8c\u8bc1|

## 8. \u590d\u73b0\u5165\u53e3

\u4ece `source/` \u6267\u884c\uff1a

```sh
npm run setup:offline
npm run check
npm test
python tests/r3_interactions.py
python tests/r3_playback.py
python tests/r3_capture.py scenes
python tests/r3_ambient_playback.py
python tests/r3_transition_trace.py
python tests/r3_extras.py
python tests/r3_performance.py
```

\u6d4f\u89c8\u5668\u811a\u672c\u9700\u8981 Python\u3001Playwright\u3001Pillow\u3001Chromium\uff1b\u5f53\u524d Linux \u663e\u793a\u6d4b\u8bd5\u4f7f\u7528 Xvfb\u3002\u8be6\u89c1 `source/tests/README.md`\u3002\u5305\u5185\u4e0d\u9644\u5b57\u4f53\u6587\u4ef6\u3002`qa/iterations/` \u4ec5\u4e3a\u4fee\u6539\u8fc7\u7a0b\u8bb0\u5f55\uff0c\u4e0d\u4f5c\u4e3a\u6700\u7ec8\u9a8c\u6536\u56fe\u3002
'''
(ROOT/'QA_REPORT.md').write_text(qa,encoding='utf-8')

# Fully local gallery. It displays existing browser captures; it is not the presentation.
title='ProxiTouch R3 \u00b7 \u6d4b\u8bd5\u4e0e\u622a\u56fe\u8bc1\u636e'
parts=[f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>',
 '<style>body{margin:0;background:#edf3f7;color:#23435a;font:16px/1.6 system-ui,sans-serif}main{max-width:1500px;margin:auto;padding:40px}h1{font-size:32px}a{color:#246184}nav{display:flex;gap:18px;flex-wrap:wrap}img{max-width:100%;height:auto;display:block}figure{margin:18px 0;border:1px solid #c7d6df;background:#fff}figcaption{padding:8px 12px;font-size:14px}details{margin:18px 0;padding:16px;border:1px solid #bccedb}summary{cursor:pointer;font-size:19px;font-weight:600}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:16px}code{overflow-wrap:anywhere}small{color:#597283}</style><main>',
 f'<h1>{title}</h1>',
 '<p>260 \u5f20\u6700\u7ec8\u539f\u59cb\u6d4f\u89c8\u5668\u622a\u56fe\uff0c\u53cc\u5206\u8fa8\u7387\u3002\u529f\u80fd\u6d4b\u8bd5\u901a\u8fc7\uff0c\u8f6f\u4ef6\u6e32\u67d3\u6d41\u7545\u5ea6\u672a\u901a\u8fc7\u3002\u5e94\u7528\u6982\u5ff5\u672a\u7ecf\u5b9e\u9a8c\u9a8c\u8bc1\u3002</p>',
 '<nav><a href="../dist/ProxiTouch-offline.html">\u6253\u5f00\u6f14\u793a</a><a href="../QA_REPORT.md">QA \u62a5\u544a</a><a href="../docs/CHANGELOG.md">\u4fee\u6539\u8bb0\u5f55</a><a href="VISUAL_REVIEW.md">\u5b9e\u9645\u770b\u56fe\u8303\u56f4</a><a href="CAPTURE_INDEX.json">\u539f\u56fe\u4e0e\u54c8\u5e0c</a></nav>',
 f'<p><small>HTML SHA-256: <code>{freeze}</code></small></p>',
 '<figure><a href="VISUAL_WALL.png"><img src="VISUAL_WALL.png" alt="R3 actual WebGL screenshots"></a><figcaption>\u672c\u8f6e\u4fee\u6539\u9875\u9762\u603b\u89c8\uff08\u5b9e\u9645\u6e32\u67d3\uff09</figcaption></figure>']
for r in ['1920x1080','2560x1440']:
 parts.append(f'<details><summary>{r} \u8054\u7cfb\u8868\u4e0e\u8f6c\u573a</summary>')
 for p in sorted((Q/'review'/r).glob('*.png')):
  rel=p.relative_to(Q).as_posix()
  parts.append(f'<figure><a href="{rel}"><img loading="lazy" src="{rel}" alt="{p.stem}"></a><figcaption>{p.stem}</figcaption></figure>')
 parts.append('</details>')
 for mode in ['scenes','transitions','ambient','explore']:
  group=[c for c in captures if c['file'].startswith(f'{mode}/{r}/')]
  parts.append(f'<details><summary>{r} / {mode} \u00b7 {len(group)} \u5f20\u539f\u56fe</summary><div class="grid">')
  for c in group:
   rel=c['file'];parts.append(f'<figure><a href="{rel}"><img loading="lazy" src="{rel}" alt="{html.escape(rel)}"></a><figcaption>{Path(rel).stem} | phase={c["scenePhase"]} | ambient={c["ambientSeconds"]}s</figcaption></figure>')
  parts.append('</div></details>')
parts.append('<details><summary>\u539f\u59cb\u6d4b\u8bd5\u62a5\u544a</summary><ul>')
for rel in ['RELEASE_SUMMARY.json','ENVIRONMENT.json','r3-model-tests.json','interactions/r3-report.json','full-playback/report.json','ambient-live/report.json','live-transitions/report.json','extras/report.json','regression/report.json','performance/report.json','rebuild/report.json','VISUAL_REVIEW.json']:
 parts.append(f'<li><a href="{rel}">{rel}</a></li>')
parts.append('</ul></details><p><small>\u8054\u7cfb\u8868\u4e0d\u7b49\u4e8e\u6240\u6709\u539f\u56fe\u9010\u50cf\u7d20\u9a8c\u6536\u3002\u5165\u53e3\u653f\u7b56\u3001\u6d41\u7545\u5ea6\u548c\u5b9e\u9a8c\u8fb9\u754c\u8bf7\u9605\u8bfb QA \u62a5\u544a\u3002</small></p></main></html>')
(Q/'INDEX.html').write_text('\n'.join(parts),encoding='utf-8')
print(json.dumps(summary,indent=2))
