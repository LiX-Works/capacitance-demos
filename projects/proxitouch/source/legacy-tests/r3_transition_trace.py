"""Observe every actually rendered SAFE frame in S20 and S22, without seeking.
Supplementary to the quarter/dense-phase full-resolution screenshots and
100-step deterministic geometry checks; not a claim of exhaustive raster QA.
"""
from harness import *
import json,hashlib,sys
out=ROOT/'qa/live-transitions';out.mkdir(parents=True,exist_ok=True)
checks=[];sha=hashlib.sha256((ROOT/'dist/ProxiTouch-offline.html').read_bytes()).hexdigest()
with sync_playwright() as p:
 b,page,errors=launch(p);page.evaluate('__PT.quality("safe");__PT.captureMode(false)')
 try:
  for sid in ['S20','S22']:
   page.evaluate('''s=>{const a=__PT.app;__PT.goTo(s,0);window.__r3Trace=[];const original=a.renderer.frame.bind(a.renderer);window.__r3Restore=()=>a.renderer.frame=original;a.renderer.frame=(...args)=>{const ar=a.worlds.array,hero= a.worlds.grasp;window.__r3Trace.push({scene:a.def.id,phase:a.phase,main:!!a.animation,arrayCount:a.state.arrayCount,merge:a.state.merge,independentMatrices:Array.from(ar.independent.matrices.slice(0,16*16)),independentAlpha:Array.from(ar.independent.colors),array:ar.diagnostics(),hero:hero.diagnostics()});return original(...args);};a.animate(); }''',sid)
   page.wait_for_function('__PT.app.phase===1&&!__PT.app.animation',timeout=35000)
   trace=page.evaluate('window.__r3Restore();window.__r3Trace');page.screenshot(path=str(out/(sid+'-completed.png')))
   ok=len(trace)>8 and all(trace[i]['phase']>=trace[i-1]['phase'] for i in range(1,len(trace))) and trace[-1]['phase']==1
   detail={'actuallyRenderedFrames':len(trace)}
   if sid=='S20':
    merged=[t for t in trace if .34<=t['phase']<=.61];holds=[t for t in trace if .61<t['phase']<.71]
    ok=ok and len(merged)>=2 and len(holds)>=1
    if merged:
     m=merged[0]['independentMatrices'];outer=[i for i in range(16) if abs(m[i*16+12])>2.99 or abs(m[i*16+14])>2.99]
     deviation=max(abs(t['independentMatrices'][i*16+j]-m[i*16+j]) for t in merged for i in outer for j in [0,1,2,4,5,6,8,9,10,12,13,14])
     ok=ok and len(outer)==8 and deviation<1e-6
     detail.update({'mergeRenderedFrames':len(merged),'stableFourRenderedFrames':len(holds),'outerRailMatrixMaximumDeviation':deviation})
    ok=ok and all(t['arrayCount']<=4.00001 or t['merge']>=.999 for t in trace)
   else:
    ok=ok and all(trace[i]['hero']['spread']<=trace[i-1]['hero']['spread']+1e-8 for i in range(1,len(trace))) and all(t['hero']['eggIntact'] for t in trace)
    stages=list(dict.fromkeys(t['hero']['stage'] for t in trace));ok=ok and stages==['approach','touch','pressure'];detail['stages']=stages
    final=trace[-1]['hero'];page.wait_for_timeout(500);ok=ok and final==page.evaluate('__PT.app.worlds.grasp.diagnostics()')
   checks.append({'scene':sid,'passed':ok,'detail':detail,'trace':trace});print(sid,'PASS' if ok else 'FAIL',detail,flush=True)
   (out/'report.json').write_text(json.dumps({'sourceSha256':sha,'quality':'safe','timeIsReal':True,'checks':checks,'errors':errors},indent=2))
 finally:b.close()
if errors or any(not c['passed'] for c in checks):sys.exit(1)
