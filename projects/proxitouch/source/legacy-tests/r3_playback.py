"""Unaccelerated real browser playback. No seeking after the start."""
from harness import *
import json,hashlib,time,sys
folder=ROOT/'qa/full-playback';folder.mkdir(parents=True,exist_ok=True)
sha=hashlib.sha256((ROOT/'dist/ProxiTouch-offline.html').read_bytes()).hexdigest()
with sync_playwright() as p:
 b,page,errors=launch(p);quality=os.environ.get('PT_PLAYBACK_QUALITY','high');page.evaluate('(q)=>__PT.quality(q)',quality)
 try:
  page.evaluate("window.__PT.goTo('S00',1);window.__PT.app.history=[];window.__PT.app.record()")
  start=time.monotonic();page.keyboard.press('p');samples=[];last='';complete=False
  while time.monotonic()-start<160:
   s=page.evaluate('({scene:__PT.snapshot().scene,phase:__PT.app.phase,fullAuto:__PT.app.fullAuto,playing:!!__PT.app.animation,time:performance.now()})')
   if s['scene']!=last:print(s['scene'],round(time.monotonic()-start,1),flush=True);last=s['scene']
   samples.append(s);(folder/'progress.json').write_text(json.dumps({'elapsed':time.monotonic()-start,'sample':s,'errors':errors},indent=2))
   if s['scene']=='S22' and s['phase']==1 and not s['fullAuto']:
    complete=True;break
   page.wait_for_timeout(800)
  elapsed=time.monotonic()-start;page.evaluate('__PT.flush()');page.screenshot(path=str(folder/'completed-S22.png'))
  history=page.evaluate('__PT.app.history');d=page.evaluate('__PT.diagnostics()');visited=list(dict.fromkeys(h['scene'] for h in history));ends=list(dict.fromkeys(h['scene'] for h in history if h['phase']==1))
  data={'sourceSha256':sha,'accelerated':False,'quality':d['quality'],'complete':complete,'elapsedSeconds':elapsed,'visitedScenes':visited,'stableEnds':ends,'samples':samples,'history':history,'diagnostic':d,'errors':errors,'requests':page.pt_requests}
  (folder/'report.json').write_text(json.dumps(data,ensure_ascii=False,indent=2));print('COMPLETE',complete,'SCENES',len(visited),'ENDS',len(ends),'SECONDS',elapsed,flush=True)
 finally:b.close()
if not complete or len(visited)!=23 or len(ends)!=23 or errors:sys.exit(1)
