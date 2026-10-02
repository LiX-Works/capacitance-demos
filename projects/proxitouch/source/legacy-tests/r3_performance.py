"""Actual active WebGL RAF cadence; no GPU extrapolation or screenshot work during samples."""
from harness import *
import json,hashlib,statistics
out=ROOT/'qa/performance';out.mkdir(parents=True,exist_ok=True)
sha=hashlib.sha256((ROOT/'dist/ProxiTouch-offline.html').read_bytes()).hexdigest();records=[]
with sync_playwright() as p:
 b,page,errors=launch(p)
 try:
  for quality in ['high','safe']:
   page.evaluate('q=>__PT.quality(q)',quality)
   for sid in ['S21','S22','S07','S18']:
    page.evaluate('''s=>{__PT.captureMode(false);__PT.goTo(s,.60);const a=__PT.app;if(s==='S21'||s==='S22'){a.animation={from:.60,to:1,start:performance.now(),duration:12000};}else{a.phase=1;}a.dirty=true;}''',sid)
    page.wait_for_timeout(1000)
    data=page.evaluate('''()=>new Promise(resolve=>{let start,last;const dt=[];function sample(t){if(start===undefined){start=last=t;requestAnimationFrame(sample);return;}dt.push(t-last);last=t;if(t-start<4500)requestAnimationFrame(sample);else{__PT.stop();resolve({elapsedMs:t-start,intervals:dt});}}requestAnimationFrame(sample);})''')
    d=page.evaluate('__PT.diagnostics()');xs=[x for x in data['intervals'] if x>0]
    rec={'scene':sid,'quality':quality,'elapsedMs':data['elapsedMs'],'activeIntervals':len(xs),'averageFPS':len(xs)*1000/data['elapsedMs'],'medianFrameMs':statistics.median(xs),'p95FrameMs':sorted(xs)[min(len(xs)-1,int(.95*len(xs)))],'intervals':xs,'diagnostic':d};records.append(rec)
    (out/'report.json').write_text(json.dumps({'sourceSha256':sha,'method':'1 s warmup, at least 4.5 s actual active RAF intervals. S21/S22 use the real main-animation path with a 12 s time-stretched pressure slice (.60 onward) for enough samples; S07/S18 use their normal live ambient clocks. No screenshot encoding during sample. Full-speed timing is separately checked by the unaccelerated complete playback.','width':1920,'height':1080,'hardwareGPU':False,'errors':errors,'measurements':records},ensure_ascii=False,indent=2));print(sid,quality,round(rec['averageFPS'],2),'FPS',len(xs),'intervals',flush=True)
 finally:b.close()
