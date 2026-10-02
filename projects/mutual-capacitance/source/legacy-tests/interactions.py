from harness import *
import json,hashlib,sys,time
from PIL import Image,ImageChops
R=ROOT/'qa/interactions';R.mkdir(parents=True,exist_ok=True)
checks=[];errors=[]
def check(name,ok,detail=None):checks.append({'name':name,'passed':bool(ok),'detail':detail});print('PASS'if ok else'FAIL',name,flush=True)
with sync_playwright() as p:
 b,page,errors=launch(p)
 try:
  page.evaluate('__LAB.goTo("02",.4);__LAB.captureMode(true)');before=page.evaluate('__LAB.snapshot()');page.evaluate('__LAB.flush()');page.screenshot(path=str(R/'before-explore.png'))
  page.keyboard.press('e');check('E opens Explore',page.evaluate('__LAB.snapshot().explore'))
  page.locator('#theta').fill('42.25');page.locator('#theta').dispatch_event('input');s=page.evaluate('__LAB.snapshot()');check('Slider shares exact theta with actual rigid rotation',abs(s['state']['theta']-42.25)<1e-12 and abs(page.evaluate('__LAB.app.experiment.hinge.rotation[2]')-42.25*3.141592653589793/180)<1e-12);check('Non-node theta is explicitly interpolated',s['sample']['interpolated'] and s['sample']['bracket']==[40,45],s['sample'])
  page.locator('[data-angle="90"]').click();check('Quick angle selects a real numerical node',page.evaluate('__LAB.snapshot().sample.exact'))
  c0=page.evaluate('__LAB.snapshot().sample.C_F');page.locator('#material-toggle').click();s=page.evaluate('__LAB.snapshot()');check('Material control updates geometry and capacitance',s['state']['er']==4 and s['sample']['C_F']>c0 and page.evaluate('__LAB.app.experiment.dielectric.visible'))
  c1=s['sample']['C_F'];page.locator('#width-toggle').click();check('Full-width display does not change physical capacitance',page.evaluate('__LAB.snapshot().sample.C_F')==c1 and page.evaluate('__LAB.app.experiment.visibleWidth')==.12)
  page.evaluate('__LAB.flush()');page.screenshot(path=str(R/'fullwidth-90.png'))
  for f in ['potential','strength','lines']:
   page.locator('[data-field="'+f+'"]').click();check('Field mode '+f,page.evaluate('__LAB.snapshot().state.field')==f);page.evaluate('__LAB.flush()');page.screenshot(path=str(R/('explore-'+f+'.png')))
  old=page.evaluate('__LAB.snapshot().camera');page.mouse.move(1130,470);page.mouse.down();page.mouse.move(1210,500,steps=8);page.mouse.up();check('Pointer orbit changes the actual camera',page.evaluate('__LAB.snapshot().camera')!=old)
  old=page.evaluate('__LAB.snapshot().camera');page.mouse.wheel(0,180);page.wait_for_timeout(200);check('Wheel zoom changes camera',page.evaluate('__LAB.snapshot().camera')!=old)
  page.locator('#theta').focus();page.keyboard.press('Escape');after=page.evaluate('__LAB.snapshot()');check('Escape restores original scene, phase, geometry and camera',all(before[k]==after[k]for k in ['scene','phase','state','camera','sample']))
  page.evaluate('__LAB.flush()');page.screenshot(path=str(R/'after-explore.png'));diff=ImageChops.difference(Image.open(R/'before-explore.png').convert('RGB'),Image.open(R/'after-explore.png').convert('RGB'));check('Explore return is pixel-identical',diff.getbbox()is None,{'differenceBox':diff.getbbox()})
  page.evaluate('__LAB.goTo("01",0,true)');page.wait_for_timeout(500);page.keyboard.press('Space');s=page.evaluate('__LAB.snapshot()');phase=s['phase'];check('Space pauses an intermediate animation',not s['playing']and 0<phase<1);page.wait_for_timeout(400);check('Paused phase remains stable',page.evaluate('__LAB.snapshot().phase')==phase);page.keyboard.press('Space');page.wait_for_timeout(350);check('Space resumes from the paused phase',page.evaluate('__LAB.snapshot().phase')>phase)
  page.keyboard.press('ArrowRight');s=page.evaluate('__LAB.snapshot()');check('First Right finishes current main animation',s['scene']=='01'and s['phase']==1 and not s['playing']);page.keyboard.press('ArrowRight');check('Second Right starts the next scene',page.evaluate('__LAB.snapshot().scene')=='02');page.keyboard.press('ArrowLeft');check('Left returns to a stable current-scene start',page.evaluate('__LAB.snapshot().phase')==0 and not page.evaluate('__LAB.snapshot().playing'));page.keyboard.press('ArrowLeft');check('Left at start goes to previous final frame',page.evaluate('__LAB.snapshot().scene')=='01'and page.evaluate('__LAB.snapshot().phase')==1)
  page.keyboard.press('r');page.wait_for_timeout(350);check('R replays the actual animation',page.evaluate('__LAB.snapshot().playing')and page.evaluate('__LAB.snapshot().phase')<1);page.evaluate('__LAB.stop()')
  page.evaluate('__LAB.captureMode(false)');page.keyboard.press('g');check('Scene menu contains all twelve pages',page.locator('.menu-grid button').count()==12);page.locator('.menu-grid button').nth(8).click();check('Menu selects requested scene',page.evaluate('__LAB.snapshot().scene')=='09');page.evaluate('__LAB.goTo("09",1)')
  page.locator('#about-toggle').click();check('Parameter/method panel includes SI dimensions and modelling limitations',page.locator('.about').is_visible() and '120' in page.locator('.about-scroll').inner_text());page.keyboard.press('Escape');check('Esc closes parameter dialog',not page.locator('.about').is_visible())
  page.keyboard.press('t');check('T collapses explanations',page.locator('#app').evaluate('e=>e.classList.contains("copy-collapsed")'));page.keyboard.press('t');check('T restores explanations',not page.locator('#app').evaluate('e=>e.classList.contains("copy-collapsed")'))
  page.locator('#chart-scale').click();check('Logarithmic axis is available',page.evaluate('__LAB.app.hud.chart.log'));page.locator('#chart-scale').click()
  for w,h in [(2560,1440),(1366,768)]:
   page.set_viewport_size({'width':w,'height':h});page.wait_for_timeout(200)
   for sid in ['02','09','11']:
    page.evaluate('(s)=>{__LAB.goTo(s,1);__LAB.flush()}',sid);page.screenshot(path=str(R/f'{w}-{sid}.png'));d=page.evaluate('__LAB.diagnostics()');check(f'{w} scene {sid} bounded layout',not d['overflow']and not d['documentOverflow']and not d['labelOverlaps']and not d['mathErrors'],d)
  check('No browser JS or console errors',not errors,errors)
 finally:b.close()
(R/'report.json').write_text(json.dumps({'sourceSha256':hashlib.sha256((ROOT/'dist/Capacitance-Lab-offline.html').read_bytes()).hexdigest(),'checks':checks,'errors':errors},ensure_ascii=False,indent=2))
if any(not c['passed']for c in checks):sys.exit(1)
