from harness import *
import json,time,hashlib,sys
out=ROOT/'qa/playback';out.mkdir(parents=True,exist_ok=True)
report={'sourceSha256':hashlib.sha256((ROOT/'dist/Capacitance-Lab-offline.html').read_bytes()).hexdigest(),'unaccelerated':True,'start':'Home then P','quality':'high'}
with sync_playwright() as p:
 b,page,errors=launch(p)
 page.evaluate('''()=>{__LAB.captureMode(true);const app=__LAB.app;window.__telemetry={order:[],scenes:{}};const draw=app.draw.bind(app);app.draw=()=>{draw();const t=__telemetry,id=app.scene.id;if(t.order.at(-1)!==id)t.order.push(id);const s=t.scenes[id]??={min:1,max:0,frames:0,first:performance.now(),last:0};s.min=Math.min(s.min,app.phase);s.max=Math.max(s.max,app.phase);s.frames++;s.last=performance.now();}}''')
 start=time.time();page.keyboard.press('Home');page.keyboard.press('p');last=''
 try:
  while time.time()-start<240:
   page.wait_for_timeout(350)
   s=page.evaluate('({scene:__LAB.app.scene.id,phase:__LAB.app.phase,auto:__LAB.app.auto,playing:!!__LAB.app.animation})')
   if s['scene']!=last:print(s['scene'],round(time.time()-start,2),flush=True);last=s['scene']
   if s['scene']=='12' and s['phase']==1 and not s['auto'] and not s['playing']:break
  else:raise RuntimeError('Playback timeout')
  page.evaluate('__LAB.flush()');page.screenshot(path=str(out/'completed.png'))
  report.update({'elapsedSeconds':time.time()-start,'finalState':s,'telemetry':page.evaluate('__telemetry'),'history':page.evaluate('__LAB.app.history'),'diagnostics':page.evaluate('__LAB.diagnostics()'),'errors':errors})
  report['sceneOrderComplete']=report['telemetry']['order']==[f'{i:02d}'for i in range(1,13)]
  report['allTwelveReachedFinalState']=len(report['telemetry']['scenes'])==12 and all(s['max']==1 for s in report['telemetry']['scenes'].values())
  report['passed']=report['sceneOrderComplete']and report['allTwelveReachedFinalState']and not errors
 finally:
  b.close();(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('COMPLETE',report.get('passed'),report.get('elapsedSeconds'),flush=True)
if not report.get('passed'):sys.exit(1)
