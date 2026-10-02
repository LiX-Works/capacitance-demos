from harness import *
import json,time,hashlib
from PIL import Image,ImageChops,ImageStat,ImageDraw
out=ROOT/'qa/explore';out.mkdir(parents=True,exist_ok=True)
checks=[];captures=[]
def check(name,condition,detail=None):
 checks.append({'name':name,'pass':bool(condition),'detail':detail});print('PASS' if condition else 'FAIL',name,flush=True)
with sync_playwright() as p:
 b,page,errors=launch(p)
 def eval(s,*a):return page.evaluate(s,*a)
 def shot(name):
  page.wait_for_timeout(120);eval('window.__PT.flush()');page.screenshot(path=str(out/(name+'.png')));d=eval('window.__PT.diagnostics()');captures.append({'name':name,**d});print('SHOT',name,'overlap',d['overlayOverlapPairs'],'overflow',d['overflow'],flush=True)
 try:
  eval('window.__PT.captureMode(true)');eval("window.__PT.goTo('D14',.64)");before=eval('window.__PT.snapshot()');shot('return-before')
  page.keyboard.press('e');check('E enters Explore',eval('window.__PT.snapshot().mode')=='explore')
  for view in ['device','field','micro','nano','signal','exploded']:
   page.locator('[data-view="'+view+'"]').click()
   for depth in [-.55,0,.72]:
    page.locator('#depth-input').evaluate('(e,v)=>{e.value=v;e.dispatchEvent(new Event("input",{bubbles:true}))}',depth)
    actual=eval('window.__PT.snapshot()');check(view+' slider '+str(depth),abs(actual['model']['depth']-depth)<1e-9)
    if view=='nano':
     n=eval('({topVisible:window.__PT.app.worlds.nanoVolume.interfaceTop.visible,opacity:window.__PT.app.worlds.nanoVolume.interfaceTop.material.opacity,topY:window.__PT.app.worlds.nanoVolume.top.position[1]})')
     check('Upper EDL only after mechanical contact '+str(depth),(not n['topVisible'] or n['opacity']<.001) if depth<0 else n['topVisible'] and n['opacity']>0,n)
    shot(f'1920-{view}-'+str(depth).replace('-','m').replace('.','p'))
  # Rotation / wheel are real browser input, not direct state modification.
  page.locator('[data-view="device"]').click();old=eval('window.__PT.snapshot().camera');page.mouse.move(830,580);page.mouse.down();page.mouse.move(970,615,steps=9);page.mouse.up();new=eval('window.__PT.snapshot().camera');check('Pointer drag changes 3-D camera',new!=old)
  page.mouse.wheel(0,180);page.wait_for_timeout(150);check('Wheel changes camera distance',eval('window.__PT.snapshot().camera')!=new)
  # Esc works even while the range control has focus.
  page.locator('#depth-input').focus();page.keyboard.press('Escape');after=eval('window.__PT.snapshot()');shot('return-after')
  check('Esc restores scene / phase / model / camera exactly',all(before[k]==after[k] for k in ['scene','phase','model','camera']))
  im1=Image.open(out/'return-before.png').convert('RGB');im2=Image.open(out/'return-after.png').convert('RGB');diff=ImageChops.difference(im1,im2);stat=ImageStat.Stat(diff);check('Explore return is pixel-identical',diff.getbbox() is None,{'meanAbsoluteRGB':stat.mean,'bbox':diff.getbbox()})
  page.keyboard.press('r');check('R restores canonical beginning',eval('window.__PT.snapshot().phase')==0)
  page.keyboard.press('ArrowRight');page.wait_for_timeout(600);check('Next runs a real animated interval',0<eval('window.__PT.snapshot().phase')<1)
  page.keyboard.press('ArrowLeft');check('Previous cancels and returns canonical beat',eval('window.__PT.snapshot().phase')==0 and not eval('window.__PT.snapshot().playing'))
  # Fundamentals instrument cannot expose the future product.
  eval("window.__PT.goTo('F10',1)");page.keyboard.press('e')
  check('Product / exploded buttons disabled before Design',page.locator('[data-view="device"]').is_disabled() and page.locator('[data-view="exploded"]').is_disabled())
  for view in ['field','micro','nano','signal']:
   page.locator('[data-view="'+view+'"]').click();shot('fundamentals-'+view)
  check('Fundamentals signal title is mutual-only',page.locator('h1').inner_text()=='\u4e92\u7535\u5bb9\u4fe1\u53f7')
  page.keyboard.press('Escape');page.keyboard.press('t');check('Speaker script is available',page.locator('.speaker-notes').is_visible() and len(page.locator('.speaker-notes p').first.inner_text())>40);shot('speaker-notes');page.keyboard.press('Escape')
  page.keyboard.press('g');check('Chapter menu has all 46 scenes',page.locator('.chapter-group>button').count()==46);page.locator('.chapter-group>button').filter(has_text='D23').click();check('Chapter selection loads D23',eval('window.__PT.snapshot().scene')=='D23')
  # Automatic Explore sweep should change the unified state, then stop.
  page.keyboard.press('e');page.locator('#auto-button').click();a=eval('window.__PT.snapshot().model.depth');page.wait_for_function('(d)=>Math.abs(window.__PT.snapshot().model.depth-d)>.02',arg=a,timeout=12000);z=eval('window.__PT.snapshot().model.depth');check('Explore automatic sweep changes state',abs(a-z)>.01,{'before':a,'after':z});page.locator('#auto-button').click();a=eval('window.__PT.snapshot().model.depth');page.wait_for_timeout(200);check('Explore automatic sweep pauses exactly',a==eval('window.__PT.snapshot().model.depth'))
  for q in ['medium','safe','high']:
   page.locator('#quality-select').select_option(q);check('Quality '+q,eval('window.__PT.snapshot().quality')==q)
  page.locator('#quality-select').evaluate('e=>e.blur()');page.keyboard.press('Escape')
  # Actual resize at high quality, not scaled images.
  page.set_viewport_size({'width':2560,'height':1440});page.wait_for_timeout(250);page.keyboard.press('e');eval('window.__PT.setDepth(.65)')
  for view in ['device','field','micro','nano','signal','exploded']:
   page.locator('[data-view="'+view+'"]').click();shot('2560-'+view)
  page.keyboard.press('Escape');eval('window.__PT.captureMode(false)');page.locator('#fullscreen-button').click();page.wait_for_timeout(200);fullscreen=eval('({active:!!document.fullscreenElement,notice:document.querySelector(".toast").textContent})');check('Fullscreen command succeeds or fails gracefully',fullscreen['active'] or bool(fullscreen['notice']),fullscreen)
  if fullscreen['active']:eval('document.exitFullscreen()')
  check('No JS / console errors',not errors,errors)
  check('All captured layouts have no overflow or DOM collisions',all(not c['overflow'] and not c['documentOverflow'] and not c['overlayOverlapPairs'] and c['labelOverlapCount']==0 and c['labelOutOfBounds']==0 and c['mathErrors']==0 and c['glError']==0 for c in captures))
 finally:
  report={'sourceSha256':hashlib.sha256((ROOT/'dist/ProxiTouch-offline.html').read_bytes()).hexdigest(),'checks':checks,'captures':captures,'errors':errors};(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));b.close()
# Legible 6-up walls, with each image also retained at its actual viewport.
for group in ['device','field','micro','nano','signal','exploded']:
 names=[c['name'] for c in captures if c['name'].startswith('1920-'+group)]
 wall=Image.new('RGB',(1800,1064),'#eff4f7');d=ImageDraw.Draw(wall)
 for i,name in enumerate(names):
  x=(i%2)*900;y=(i//2)*532;im=Image.open(out/(name+'.png')).convert('RGB').resize((900,506));wall.paste(im,(x,y+26));d.text((x+14,y+8),name,fill='#24465c')
 wall.save(out/(group+'-sheet.png'))
print('DONE',len(checks),'checks',sum(not c['pass'] for c in checks),'failed',len(captures),'captures',flush=True)
