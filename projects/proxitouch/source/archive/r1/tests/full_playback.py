"""Real-time, unaccelerated public-keyboard playback of every scene and beat."""
from harness import *
import json,time,hashlib
out=ROOT/'qa/full-playback';out.mkdir(parents=True,exist_ok=True)
start=time.time();report={'accelerated':False,'entry':'Keyboard Home, then P','quality':'high','sourceSha256':hashlib.sha256((ROOT/'dist/ProxiTouch-offline.html').read_bytes()).hexdigest()}
with sync_playwright() as p:
 b,page,errors=launch(p)
 page.evaluate('''() => {
 const a=window.__PT.app;a.capture=true;window.__playbackTelemetry={order:[],scenes:{},start:performance.now(),draws:0};
 const original=a.draw.bind(a);a.draw=()=>{original();const t=window.__playbackTelemetry,id=a.def.id;t.draws++;if(t.order.at(-1)!==id)t.order.push(id);const d=t.scenes[id]??={samples:0,min:1,max:0,phases:[],first:performance.now(),last:0};d.samples++;d.min=Math.min(d.min,a.phase);d.max=Math.max(d.max,a.phase);d.last=performance.now();if(d.phases.length<160&&a.animation)d.phases.push(Number(a.phase.toFixed(5)));};
}''')
 page.keyboard.press('Home');page.keyboard.press('p')
 previous='';last_save=0
 try:
  while time.time()-start<1000:
   page.wait_for_timeout(500)
   state=page.evaluate('({id:window.__PT.app.def.id,phase:window.__PT.app.phase,auto:window.__PT.app.fullAuto,playing:!!window.__PT.app.animation})')
   if state['id']!=previous:
    print('SCENE',state['id'],'elapsed',round(time.time()-start,1),flush=True);previous=state['id']
   if time.time()-last_save>15:
    report.update({'elapsedSeconds':round(time.time()-start,2),'state':state,'telemetry':page.evaluate('window.__playbackTelemetry'),'history':page.evaluate('window.__PT.app.history'),'errors':errors})
    (out/'progress.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));last_save=time.time()
   if state['id']=='D23' and state['phase']==1 and not state['auto'] and not state['playing']:break
  else:raise RuntimeError('Full playback did not finish within 1000 seconds')
  page.wait_for_timeout(3000);page.evaluate('window.__PT.flush()');page.screenshot(path=str(out/'completed-D23.png'))
  report.update({'elapsedSeconds':round(time.time()-start,2),'state':state,'telemetry':page.evaluate('window.__playbackTelemetry'),'history':page.evaluate('window.__PT.app.history'),'errors':errors,'diagnostics':page.evaluate('window.__PT.diagnostics()')})
  expected=page.evaluate('window.__PT.scenes.map(s=>s.id)');report['orderComplete']=report['telemetry']['order']==expected
  report['everySceneReachedEnd']=all(v['max']==1 for v in report['telemetry']['scenes'].values())
  beats=page.evaluate('window.__PT.scenes');report['expectedCanonicalCount']=sum(s['beats'] for s in beats)
  reached={(x['scene'],round(x['phase'],6)) for x in report['history']};report['reachedCanonicalCount']=len(reached)
  report['complete']=report['orderComplete'] and report['everySceneReachedEnd'] and report['reachedCanonicalCount']==report['expectedCanonicalCount'] and not errors
 except Exception as e:
  report['failure']=repr(e);raise
 finally:
  (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));b.close()
print('DONE',report.get('complete'),report.get('reachedCanonicalCount'),round(time.time()-start,1),flush=True)
