"""Aggregate actual R2 evidence and create delivery navigation, not test results."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,html,math,difflib,os
ROOT=Path(__file__).resolve().parents[2];QA=ROOT/'qa'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
H=sha(ROOT/'dist/ProxiTouch-offline.html')
load=lambda p:json.loads((ROOT/p).read_text())
scenes=load('docs/SCENE_MANIFEST.json')
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
def wall(files,path,cols=3,tw=800,th=450,title=''):
 header=70 if title else 0;cellh=th+36
 im=Image.new('RGB',(cols*tw,header+math.ceil(len(files)/cols)*cellh),(238,244,248));d=ImageDraw.Draw(im)
 if title:d.text((26,23),title,font=font,fill=(39,70,91))
 for i,(p,label) in enumerate(files):
  source=Image.open(p).convert('RGB');source.thumbnail((tw-8,th-8),Image.Resampling.LANCZOS)
  x=(i%cols)*tw;y=header+(i//cols)*cellh
  d.text((x+15,y+7),label,font=small,fill=(47,78,95))
  im.paste(source,(x+(tw-source.width)//2,y+34+(th-source.height)//2))
 im.save(path)
extra=list(sorted((QA/'extras').glob('*.png')))
for i in range(0,len(extra),6):wall([(p,p.stem)for p in extra[i:i+6]],QA/'extras'/f'review-{i//6+1}.png',2,900,506,'R2 / browser interaction and layout checks')
wall([(QA/'captures/1920x1080'/f'S{n:02}.png',f'{n:02} / {label}') for n,label in [(5,'Multi-material structure'),(9,'Electric double layer'),(11,'Effective contact area'),(14,'Shared EH / EC / EB'),(18,'Time-multiplexed readout'),(19,'Continuous interaction'),(20,'Addressable shared boundaries'),(21,'Distributed sensing surface'),(22,'ProxiTouch')]],QA/'VISUAL_WALL.png',3,900,506,'ProxiTouch R2  /  actual Chromium + WebGL2 captures')
# Only count the current frozen build and actual raw captures referenced by reports.
diags=[];raw=[];reports=[];batchErrors=[]
for size in ['1920x1080','2560x1440']:
 batch=QA/'captures'/size/'batch-S00.json';b=json.loads(batch.read_text());assert b['sourceSha256']==H
 reports.append(str(batch.relative_to(ROOT)));batchErrors+=b['errors']
 for s in scenes:
  p=QA/'captures'/size/f"diagnostic-{s['id']}.json";d=json.loads(p.read_text());assert d['sourceSha256']==H
  diags.append((str(p.relative_to(ROOT)),d));raw.append(p.with_name(s['id']+'.png'))
for p in sorted((QA/'transitions').glob('S[0-9][0-9].json')):
 d=json.loads(p.read_text());assert d['sourceSha256']==H;reports.append(str(p.relative_to(ROOT)));batchErrors+=d['errors']
 for f in d['frames']:diags.append((str(p.relative_to(ROOT))+':'+str(f['phase']),f['diagnostic']));raw.append(p.parent/f['file'])
views=['device','field','micro','nano','signal','exploded']
for w in [1920,2560]:
 for v in views:
  p=QA/'explore'/f'{w}-{v}.json';d=json.loads(p.read_text());assert d['sourceSha256']==H;reports.append(str(p.relative_to(ROOT)));batchErrors+=d['errors']
  for f in d['states']:diags.append((str(p.relative_to(ROOT))+':'+str(f['depth']),f['diagnostic']));raw.append(p.parent/f['file'])
for p in sorted((QA/'extras').glob('*.json')):
 d=json.loads(p.read_text())
 if 'diagnostic' in d:
  assert d['sourceSha256']==H;diags.append((str(p.relative_to(ROOT)),d['diagnostic']));raw.append(p.with_suffix('.png'))
play=load('qa/full-playback/report.json');assert play['sourceSha256']==H;diags.append(('qa/full-playback/report.json',play['diagnostic']));raw.append(QA/'full-playback/completed-S22.png')
interaction=load('qa/interactions/report.json');assert interaction['sourceSha256']==H;raw.append(QA/'interactions/ending-after-controls.png')
extras=load('qa/extras/report.json');models=load('qa/model-tests.json');perf=load('qa/performance/report.json')
issues=[]
for name,d in diags:
 for key in ['glError','errors','overflow','documentOverflow','overlayOverlapPairs','labelOverlapCount','labelOutOfBounds','mathErrors']:
  if d.get(key):issues.append({'source':name,'metric':key,'value':d[key]})
assert not issues,issues
assert all(p.exists() for p in raw)
raw=list(dict.fromkeys(raw))
summary={'sourceSha256':H,'sourceVersion':'2.0.0','sceneCount':23,'contentPages':22,'partCounts':{'cover':1,'I':11,'II':8,'III':3},'fullPlayback':{'complete':play['complete'],'accelerated':play['accelerated'],'quality':play['quality'],'elapsedSeconds':play['elapsedSeconds'],'visited':len(play['visitedScenes']),'stableEnds':len(play['stableEnds'])},'captureCounts':{'fullScene1920':23,'fullScene2560':23,'transitionGroups':17,'transitionFrames':85,'exploreViews':6,'exploreResolutions':2,'exploreStates':36,'extras':len(extra),'fullPlaybackEnding':1,'interactionEnding':1,'totalRawPNGs':len(raw)},'diagnosticSamples':len(diags),'diagnosticIssues':issues,'browserBatchErrors':batchErrors+play['errors']+interaction['browserErrors']+extras['errors']+perf['errors'],'modelChecks':{'passed':sum(t['passed']for t in models['tests']),'total':len(models['tests'])},'interactionChecks':{'passed':sum(t['passed']for t in interaction['checks']),'total':len(interaction['checks'])},'extraChecks':{status:sum(t['status']==status for t in extras['checks'])for status in ['passed','blocked','failed']},'blockedChecks':[t for t in extras['checks']if t['status']=='blocked'],'softwareRenderer':perf['renderer'],'hardwareGPU':False,'performance':[{k:v for k,v in x.items()if k!='diagnostic'}for x in perf['measurements']],'rawCaptureFiles':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)}for p in raw],'reports':reports,'validationBoundary':'Software consistency and sampled browser evidence only. Not full physical/hardware validation. Performance remains below presentation-smoothness goals.'}
(QA/'FINAL_SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
print('FINAL SUMMARY',summary['captureCounts'],summary['extraChecks'],'diag',len(diags),'issues',len(issues))
# Source provenance: compare the recovered project, not an imagined baseline.
baseline=Path(os.environ.get('PT_BASELINE_SOURCE','/mnt/data/baseline/ProxiTouch/source'))
if not baseline.exists():
 print('Original baseline not supplied; existing source-provenance record retained.');raise SystemExit(0)
changed=[];same=[];new=[];removed=[]
for p in sorted((ROOT/'source/src').rglob('*.ts')):
 rel=p.relative_to(ROOT/'source');old=baseline/rel
 if not old.exists():new.append(str(rel))
 elif sha(old)==sha(p):same.append(str(rel))
 else:changed.append(str(rel))
for p in (baseline/'src').rglob('*.ts'):
 if not (ROOT/'source'/p.relative_to(baseline)).exists():removed.append(str(p.relative_to(baseline)))
provenance={'baselineArchive':'ProxiTouch_FINAL_DELIVERY.zip','baselineArchiveSha256':sha(Path('/mnt/data/ProxiTouch_FINAL_DELIVERY.zip')),'byteIdenticalModules':same,'modifiedExistingModules':changed,'newModules':new,'retiredFromActiveSrc':removed,'notes':'Retired Application/narration assets are archived. Existing renderer, camera, geometry, state/world organization, local build and QA harness were migrated, not replaced by a 2-D demo.'}
(ROOT/'docs/SOURCE_PROVENANCE.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2))
(ROOT/'docs/SOURCE_PROVENANCE.md').write_text('# Source provenance\n\nRecovered the complete original source from `ProxiTouch_FINAL_DELIVERY.zip`. Original archive SHA-256: `'+provenance['baselineArchiveSha256']+'`.\n\nThis release migrates the original native WebGL2 / TypeScript project. It is not a new unrelated implementation. The original scene/state/engine/geometry/model/world/UI organization and offline compiler pipeline remain recognizable. Renderer changes fix alpha handling and skip unnecessary floor shading; geometry adds controllable bevel subdivisions. Camera, math, scene graph, capacitor and legacy field assets remain byte-identical where listed.\n\n## Byte-identical active modules\n'+''.join('- `'+p+'`\n'for p in same)+'\n## Modified existing modules\n'+''.join('- `'+p+'`\n'for p in changed)+'\n## New active modules\n'+''.join('- `'+p+'`\n'for p in new)+'\n## Retired active modules\n'+''.join('- `'+p+'`\n'for p in removed)+'\nThe previous 46-scene presentation was replaced intentionally. See `MIGRATION_MAP.md`; source preservation does not require preserving obsolete scene counts or the old final Halo/Core architecture.\n')
