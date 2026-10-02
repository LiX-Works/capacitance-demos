"""Measure active-animation RAF cadence in this actual browser. No GPU extrapolation."""
from harness import *
import json,hashlib,statistics
folder=ROOT/'qa/performance';folder.mkdir(parents=True,exist_ok=True)
sha=hashlib.sha256((ROOT/'dist/ProxiTouch-offline.html').read_bytes()).hexdigest();records=[]
with sync_playwright() as p:
 b,page,errors=launch(p)
 try:
  for quality in ['high','safe']:
   page.evaluate('(q)=>__PT.quality(q)',quality)
   for scene,view in [('S08','field'),('S11','micro'),('S10','nano'),('S19','signal')]:
    page.evaluate('([s,v])=>{__PT.goTo(s,1);__PT.explore(true);__PT.view(v);__PT.setDepth(.3);__PT.app.toggleAuto();}',[scene,view]);page.wait_for_timeout(1200)
    data=page.evaluate('''()=>new Promise(resolve=>{const dt=[];let last=performance.now(),start=last;function sample(t){dt.push(t-last);last=t;if(t-start<4500)requestAnimationFrame(sample);else{__PT.app.auto=false;resolve({elapsedMs:t-start,frameCount:dt.length,intervals:dt});}}requestAnimationFrame(sample);})''')
    intervals=[x for x in data['intervals'] if x>0];med=statistics.median(intervals);d=page.evaluate('__PT.diagnostics()')
    rec={'quality':quality,'scene':scene,'view':view,'elapsedMs':data['elapsedMs'],'activeFrames':data['frameCount'],'averageFPS':data['frameCount']*1000/data['elapsedMs'],'medianFrameMs':med,'medianCadenceFPS':1000/med,'p95FrameMs':sorted(intervals)[min(len(intervals)-1,int(len(intervals)*.95))],'diagnostic':d};records.append(rec)
    (folder/'report.json').write_text(json.dumps({'sourceSha256':sha,'method':'Active-animation requestAnimationFrame wall-clock cadence, 1.2 s warm-up + 4.5 s sample. No video capture during sample.','renderer':d['renderer'],'hardwareGPU':False,'errors':errors,'measurements':records},ensure_ascii=False,indent=2));print(quality,view,round(rec['averageFPS'],2),'FPS',flush=True)
 finally:b.close()
