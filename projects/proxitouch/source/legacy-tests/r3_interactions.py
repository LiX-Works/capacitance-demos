"""Inherited R2 controls plus R3 independent-clock, boundary and capture regressions."""
from harness import *
import json,hashlib,time,sys,subprocess
from PIL import Image,ImageChops
folder=ROOT/'qa/interactions';folder.mkdir(parents=True,exist_ok=True)
subprocess.run([sys.executable,str(Path(__file__).with_name('r2_interactions.py'))],check=True)
inherited=json.loads((folder/'report.json').read_text());(folder/'inherited-r2-report.json').write_text(json.dumps(inherited,ensure_ascii=False,indent=2))
records=[];sha=hashlib.sha256((ROOT/'dist/ProxiTouch-offline.html').read_bytes()).hexdigest()
with sync_playwright() as p:
 b,page,errors=launch(p);page.set_default_timeout(15000);page.evaluate('__PT.quality("safe")')
 def check(name,condition,detail=None):
  records.append({'name':name,'passed':bool(condition),'detail':detail});print('PASS' if condition else 'FAIL',name,flush=True)
  (folder/'r3-report.json').write_text(json.dumps({'sourceSha256':sha,'inherited':inherited['checks'],'checks':records,'errors':errors},ensure_ascii=False,indent=2))
 try:
  for sid in ['S05','S07','S18']:
   page.evaluate('s=>{__PT.captureMode(false);__PT.goTo(s,1)}',sid)
   before=page.evaluate('__PT.snapshot()');page.wait_for_timeout(1600);after=page.evaluate('__PT.snapshot()')
   check(sid+' live ambient advances independently after main end',after['model']['ambientTime']>before['model']['ambientTime']+.5 and after['phase']==1 and not after['playing'],{'before':before['model']['ambientTime'],'after':after['model']['ambientTime']})
   check(sid+' ambient preserves exact camera',before['camera']==after['camera'])
   page.keyboard.press('ArrowRight');check(sid+' ambient never blocks Next',page.evaluate('__PT.snapshot().scene')!=sid)
   page.evaluate('__PT.goTo("S00",1)');state=page.evaluate('JSON.stringify({clock:__PT.app.ambient,composite:__PT.app.worlds.composite.weights,field:__PT.app.worlds.fringe.particles.instanceVersion,ions:__PT.app.worlds.nanoVolume.emphasis,mux:__PT.app.worlds.device.activeWindow})')
   page.wait_for_timeout(500);current=page.evaluate('JSON.stringify({clock:__PT.app.ambient,composite:__PT.app.worlds.composite.weights,field:__PT.app.worlds.fringe.particles.instanceVersion,ions:__PT.app.worlds.nanoVolume.emphasis,mux:__PT.app.worlds.device.activeWindow})')
   check(sid+' loop stops updating after exit',state==current)
  page.evaluate('__PT.captureMode(true);__PT.app.captureAmbient=0;__PT.goTo("S12",1);__PT.flush()');a=page.evaluate('__PT.snapshot()');page.screenshot(path=str(folder/'S12-end.png'))
  page.evaluate('__PT.goTo("S13",0);__PT.flush()');c=page.evaluate('__PT.snapshot()');page.screenshot(path=str(folder/'S13-start.png'))
  check('S12 end / S13 first frame have exactly equal fitted cameras',a['camera']==c['camera'],{'a':a['camera'],'b':c['camera']})
  box=(int(1920*.405),int(1080*.19),int(1920*.962),int(1080*.90))
  im1=Image.open(folder/'S12-end.png').convert('RGB').crop(box);im2=Image.open(folder/'S13-start.png').convert('RGB').crop(box);diff=ImageChops.difference(im1,im2);diff.save(folder/'S12-S13-model-difference.png')
  check('S12 end / S13 first model view pixel-identical',not diff.getbbox(),{'crop':box,'differenceBox':diff.getbbox()})
  page.evaluate('''()=>{__PT.captureMode(false);__PT.goTo('S12',1);const a=__PT.app;window.__boundaryTrace=[];const original=a.renderer.frame.bind(a.renderer);window.__restoreFrame=()=>a.renderer.frame=original;a.renderer.frame=(r,c,o)=>{if(a.def.id==='S13'){const names=[];r.traverse(n=>{if(n.name)names.push(n.name)});window.__boundaryTrace.push({phase:a.phase,names,other:!!o});}return original(r,c,o);};}''')
  page.keyboard.press('ArrowRight')
  page.wait_for_function('__PT.app.phase===1&&!__PT.app.animation',timeout=15000)
  trace=page.evaluate('window.__restoreFrame();window.__boundaryTrace')
  check('All actually rendered S13 playback frames contain square device, never legacy',len(trace)>1 and all('ProxiTouch-shared-square-pixel' in r['names'] and not any('legacy' in n.lower() for n in r['names']) and not r['other'] for r in trace),trace)
  page.evaluate('__PT.captureMode(true)');page.mouse.move(0,0)
  for sid,t in [('S05',7.2),('S07',2),('S18',1.5)]:
   page.evaluate('([s,t])=>{__PT.app.captureAmbient=t;__PT.goTo(s,1);__PT.flush()}',[sid,t]);file=folder/(sid+'-deterministic-a.png');page.screenshot(path=str(file));snap=page.evaluate('__PT.snapshot()')
   page.wait_for_timeout(450);page.evaluate('__PT.render();__PT.flush()');file2=folder/(sid+'-deterministic-b.png');page.screenshot(path=str(file2));snap2=page.evaluate('__PT.snapshot()')
   check(sid+' deterministic capture freezes exact pixels and state',file.read_bytes()==file2.read_bytes() and snap==snap2)
  page.evaluate('__PT.goTo("S18",1);__PT.ambientTime(0)');hc=page.locator('#instrument-bar b.active').all_text_contents();page.evaluate('__PT.ambientTime(1.5)');cb=page.locator('#instrument-bar b.active').all_text_contents()
  check('Mux UI has exactly HC | CB and follows the same phase',page.locator('#instrument-bar b').count()==2 and hc==['HC'] and cb==['CB'])
  page.evaluate('__PT.goTo("S22",.62)');before=page.evaluate('__PT.snapshot()');page.keyboard.press('e');page.locator('[data-view="signal"]').click();page.locator('#depth-input').fill('0.7');page.locator('#depth-input').dispatch_event('input');page.keyboard.press('Escape');after=page.evaluate('__PT.snapshot()')
  check('New ending Explore returns exact state and does not trap focus',all(before[k]==after[k] for k in ['scene','phase','model','camera']) and page.evaluate('document.activeElement.id')=='stage')
  page.keyboard.press('ArrowRight');check('Ending first Next completes grasp, without page reset',page.evaluate('__PT.app.phase===1&&__PT.app.def.id==="S22"'))
  check('No R3 runtime errors',not errors,errors)
 finally:b.close()
if any(not r['passed'] for r in records):sys.exit(1)
