from harness import *
import json,hashlib,time
out=ROOT/'qa/performance';out.mkdir(parents=True,exist_ok=True)
rows=[]
with sync_playwright() as p:
 b,page,errors=launch(p)
 page.evaluate('window.__PT.captureMode(true)')
 for q in ['high','medium','safe']:
  for scene in ['F08','F14','F19','D16','D20']:
   page.evaluate('([s,q])=>{window.__PT.stop();window.__PT.goTo(s,0);window.__PT.quality(q);window.__PT.flush()}',[scene,q])
   result=page.evaluate('''async()=>{const app=window.__PT.app;let intervals=[],cpu=[],last=0,start=performance.now(),i=0;return await new Promise(resolve=>{function frame(t){if(last)intervals.push(t-last);last=t;const a=performance.now();app.seek(.15+.7*((i%24)/23));app.renderer.gl.finish();cpu.push(performance.now()-a);i++;if(performance.now()-start>5000&&i>=8){const sorted=intervals.slice().sort((a,b)=>a-b), cs=cpu.slice().sort((a,b)=>a-b);resolve({frames:i,elapsedMs:performance.now()-start,medianFrameMs:sorted[Math.floor(sorted.length/2)],medianFps:1000/sorted[Math.floor(sorted.length/2)],medianRenderAndFinishMs:cs[Math.floor(cs.length/2)],p95FrameMs:sorted[Math.floor(sorted.length*.95)],intervals,renderAndFinish:cpu,diagnostics:window.__PT.diagnostics()})}else requestAnimationFrame(frame)}requestAnimationFrame(frame)})}''')
   rows.append({'scene':scene,'quality':q,**result});print(scene,q,round(result['medianFps'],2),'fps',flush=True)
   (out/'report.json').write_text(json.dumps({'sourceSha256':hashlib.sha256((ROOT/'dist/ProxiTouch-offline.html').read_bytes()).hexdigest(),'method':'Isolated browser, real rAF intervals, animated phase sampling, explicit gl.finish; includes blocking software rendering, excludes a hardware GPU claim. 1920x1080 viewport.', 'runs':rows,'errors':errors},indent=2))
 b.close()
print('DONE',len(rows),flush=True)
