"""Real-time full-cycle playback, not just a frozen-state comparison."""
from harness import *
import json,hashlib,sys
out=ROOT/'qa/ambient-live';out.mkdir(parents=True,exist_ok=True)
checks=[];sha=hashlib.sha256((ROOT/'dist/ProxiTouch-offline.html').read_bytes()).hexdigest()
with sync_playwright() as p:
 b,page,errors=launch(p);page.evaluate('__PT.quality("safe");__PT.captureMode(false)')
 try:
  for sid,seconds in [('S05',11),('S07',16),('S18',5)]:
   page.evaluate('''s=>{__PT.goTo(s,1);window.__ambientTrace=[];const a=__PT.app,o=a.renderer.frame.bind(a.renderer);window.__restore=()=>a.renderer.frame=o;a.renderer.frame=(...args)=>{window.__ambientTrace.push({t:a.state.ambientTime,phase:a.phase,main:!!a.animation,weights:{...a.worlds.composite.weights},interfaces:{...a.worlds.nanoVolume.emphasis},mux:a.worlds.device.activeWindow,dot:Array.from(a.worlds.fringe.particles.matrices.slice(12,15))});return o(...args);};}''',sid)
   page.wait_for_function('(s)=>__PT.app.state.ambientTime>=s',arg=seconds,timeout=60000)
   trace=page.evaluate('window.__restore();window.__ambientTrace')
   ok=len(trace)>5 and trace[-1]['t']>=seconds and all(r['phase']==1 and not r['main'] for r in trace)
   if sid=='S05':ok=ok and any(r['weights']['layer']>.95 for r in trace) and any(r['t']>7.2 and r['weights']['region']<.1 for r in trace)
   if sid=='S18':ok=ok and sum(trace[i]['mux']!=trace[i-1]['mux'] for i in range(1,len(trace)))>=4
   if sid=='S07':ok=ok and len(set(tuple(r['dot']) for r in trace))>20
   checks.append({'scene':sid,'passed':ok,'trace':trace});print(sid,'PASS' if ok else 'FAIL','frames',len(trace),'seconds',trace[-1]['t'],flush=True)
   (out/'report.json').write_text(json.dumps({'sourceSha256':sha,'quality':'safe','timeIsReal':True,'checks':checks,'errors':errors},indent=2))
 finally:b.close()
if errors or any(not c['passed'] for c in checks):sys.exit(1)
