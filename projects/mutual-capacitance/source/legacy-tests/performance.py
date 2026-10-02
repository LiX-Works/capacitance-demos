from harness import *
import hashlib,json
R=ROOT/'qa/performance';R.mkdir(parents=True,exist_ok=True);rows=[]
with sync_playwright() as p:
 b,page,errors=launch(p)
 try:
  for width in [1920,2560]:
   page.set_viewport_size({'width':width,'height':width*9//16})
   for q in ['high','safe']:
    for sid in ['06','09']:
     page.evaluate('(a)=>{__LAB.stop();__LAB.goTo(a[0],.2);__LAB.quality(a[1]);__LAB.captureMode(true);__LAB.flush();}',[sid,q])
     result=page.evaluate('''()=>new Promise(resolve=>{let frames=0,intervals=[],cost=[],last=0,start=performance.now();function step(t){if(last)intervals.push(t-last);last=t;const begin=performance.now();__LAB.seek(.15+.70*((frames%30)/29));__LAB.flush();cost.push(performance.now()-begin);frames++;if(performance.now()-start>=4800&&frames>=8){const x=intervals.slice().sort((a,b)=>a-b);resolve({frames,elapsedMs:performance.now()-start,medianFPS:1000/x[Math.floor(x.length/2)],averageFPS:frames*1000/(performance.now()-start),medianFrameMs:x[Math.floor(x.length/2)],p95FrameMs:x[Math.floor(.95*x.length)],intervals,renderAndFinishMs:cost,diagnostics:__LAB.diagnostics()})}else requestAnimationFrame(step)}requestAnimationFrame(step)})''')
     rows.append({'width':width,'quality':q,'scene':sid,**result});print(width,q,sid,round(result['medianFPS'],2),'median FPS',flush=True)
     (R/'report.json').write_text(json.dumps({'sourceSha256':hashlib.sha256((ROOT/'dist/Capacitance-Lab-offline.html').read_bytes()).hexdigest(),'method':'Isolated Chromium, active phase changes every RAF, explicit gl.finish, no screenshot or concurrent rendering jobs during the measurement. Real elapsed frame intervals, not CPU submission time.','hardwareGPU':False,'measurements':rows,'errors':errors},ensure_ascii=False,indent=2))
 finally:b.close()
