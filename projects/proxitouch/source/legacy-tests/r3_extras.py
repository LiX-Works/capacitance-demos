"""Resize, real gestures, native file and HTTP loading, all recorded separately."""
from harness import *
import json,hashlib,subprocess,urllib.request,time,sys
folder=ROOT/'qa/extras';folder.mkdir(parents=True,exist_ok=True)
sha=hashlib.sha256((ROOT/'dist/ProxiTouch-offline.html').read_bytes()).hexdigest();records=[]
with sync_playwright() as p:
 b,page,errors=launch(p);page.set_default_timeout(10000);page.evaluate('__PT.captureMode(true)')
 try:
  def check(name,passed,detail=None):
   status='passed' if passed else 'blocked' if 'ERR_BLOCKED_BY_ADMINISTRATOR' in str(detail) else 'failed'
   records.append({'name':name,'passed':bool(passed),'status':status,'detail':detail});print(status.upper(),name,flush=True)
   (folder/'report.json').write_text(json.dumps({'sourceSha256':sha,'errors':errors,'checks':records},ensure_ascii=False,indent=2))
  def capture(name):
   page.evaluate('__PT.flush()');page.screenshot(path=str(folder/(name+'.png')));d=page.evaluate('__PT.diagnostics()');(folder/(name+'.json')).write_text(json.dumps({'sourceSha256':sha,'diagnostic':d},ensure_ascii=False,indent=2));return d
  page.evaluate("__PT.goTo('S13',1)");page.locator('.copy-scroll').evaluate('(e)=>e.scrollTop=e.scrollHeight');capture('body-scrolled')
  page.keyboard.press('t');d=capture('body-collapsed');check('Collapsed copy does not obstruct geometry',not d['bodyDefaultVisible'] and not d['overflow']);page.keyboard.press('t')
  page.keyboard.press('g');capture('chapter-menu');page.keyboard.press('Escape');page.locator('#about-button').click();capture('about');page.keyboard.press('Escape')
  page.evaluate("__PT.goTo('S17',.7)");before=page.evaluate('__PT.snapshot()');page.keyboard.press('e');page.locator('[data-view="device"]').click();a=page.evaluate('__PT.snapshot().camera')
  zone=page.locator('#model-zone').bounding_box();x=zone['x']+zone['width']*.55;y=zone['y']+zone['height']*.58
  page.mouse.move(x,y);page.mouse.down();page.mouse.move(x+90,y-40,steps=8);page.mouse.up();c=page.evaluate('__PT.snapshot().camera');check('Actual pointer orbit changes camera',a!=c)
  page.mouse.wheel(0,-140);page.wait_for_timeout(500);z=page.evaluate('__PT.snapshot().camera');check('Actual wheel zoom changes camera',c!=z);capture('explore-orbit-zoom')
  page.locator('#reset-button').click();check('Reset clears orbit override and resets interaction',page.evaluate('__PT.app.exploreCamera===undefined && __PT.app.depth===-.4'))
  d0=page.evaluate('__PT.snapshot().model.depth');page.locator('#auto-button').click();page.wait_for_timeout(1500);d1=page.evaluate('__PT.snapshot().model.depth');page.locator('#auto-button').click();check('Explore auto interaction changes depth',abs(d1-d0)>.001,{'a':d0,'b':d1})
  page.keyboard.press('Escape');after=page.evaluate('__PT.snapshot()');check('Explore orbit, zoom and auto restore exact presentation',all(before[k]==after[k] for k in ['scene','phase','model','camera','notes']))
  for width,scene in [(1366,'S10'),(1366,'S12'),(1366,'S18'),(1366,'S19'),(2560,'S19')]:
   page.set_viewport_size({'width':width,'height':round(width*9/16)});page.evaluate('s=>__PT.goTo(s,1)',scene);d=capture(f'{width}-{scene}');check(f'Resize {width} {scene}',not d['overflow'] and not d['documentOverflow'] and not d['labelOverlapCount'],d)
  page.set_viewport_size({'width':1920,'height':1080});page.evaluate("__PT.quality('safe');__PT.goTo('S19',.75)");d=capture('safe-S19');check('SAFE renders actual scene without errors',d['quality']=='safe' and d['glError']==0 and not d['errors'],d)
  for quality in ['high','safe']:
   for width in [1920,2560]:
    page.set_viewport_size({'width':width,'height':width*9//16});page.evaluate('q=>{__PT.quality(q);__PT.goTo("S22",1)}',quality);d=capture(f'hero-{quality}-{width}');check(f'Hero {quality} {width} finite and unclipped',not d['overflow'] and not d['labelOverlapCount'] and d['glError']==0,d)
  # Allowed offline document loading, separate from native URL navigation below.
  page.context.set_offline(True);page.pt_requests.clear()
  page.close();page=b.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1);page.pt_requests=[];page.context.set_offline(True);page.on('request',lambda r:page.pt_requests.append({'url':r.url}));page.on('pageerror',lambda e:errors.append(str(e)));page.set_content((ROOT/'dist/ProxiTouch-offline.html').read_text(),wait_until='load',timeout=30000)
  page.wait_for_function('window.__PT?.ready',timeout=30000);page.evaluate("__PT.goTo('S14',1)");d=capture('offline-payload')
  check('Offline HTML payload renders with network disabled and no requests',d['glError']==0 and not d['errors'] and not page.pt_requests,{'requests':page.pt_requests.copy(),'diagnostic':d})
  page.context.set_offline(False)
  # The self-contained file is tested directly, with network disabled, not only set_content.
  off=b.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1);off.context.set_offline(True);requested=[];off.on('request',lambda r:requested.append(r.url));offerrors=[];off.on('pageerror',lambda e:offerrors.append(str(e)))
  try:
   off.goto((ROOT/'dist/ProxiTouch-offline.html').as_uri(),wait_until='load',timeout=15000);off.wait_for_function('window.__PT?.ready',timeout=15000);off.evaluate("__PT.goTo('S14',1);__PT.flush()");off.screenshot(path=str(folder/'native-file-offline.png'))
   check('Native file URL runs with network disabled',True,{'requests':requested,'errors':offerrors,'diagnostic':off.evaluate('__PT.diagnostics()')})
  except Exception as exc:check('Native file URL runs with network disabled',False,{'error':str(exc),'requests':requested})
  finally:off.close();page.context.set_offline(False)
  env=dict(os.environ,PORT='4174');server=subprocess.Popen(['node','scripts/serve.mjs'],cwd=str(ROOT/'source'),env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  try:
   for _ in range(30):
    try:urllib.request.urlopen('http://127.0.0.1:4174/',timeout=1);break
    except Exception:time.sleep(.1)
   routes=[]
   for route in ['/','/app.js','/style.css','/ProxiTouch-offline.html','/js/models/Device.js','/js/scenes/copy.js']:
    with urllib.request.urlopen('http://127.0.0.1:4174'+route,timeout=4) as res:routes.append({'path':route,'status':res.status,'bytes':len(res.read()),'type':res.headers.get('Content-Type')})
   check('Built HTTP output serves six required routes',all(x['status']==200 for x in routes),routes)
   http=b.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
   try:
    http.goto('http://127.0.0.1:4174/',wait_until='load',timeout=15000);http.wait_for_function('window.__PT?.ready',timeout=15000);http.evaluate("__PT.goTo('S20',1);__PT.flush()");http.screenshot(path=str(folder/'http-built-index.png'));check('Actual browser loads built HTTP index',True,http.evaluate('__PT.diagnostics()'))
   except Exception as exc:check('Actual browser loads built HTTP index',False,str(exc))
   finally:http.close()
  finally:server.terminate();server.wait(timeout=5)
  check('No JavaScript console errors in extras',not errors,errors)
 finally:b.close()
if any(x['status']=='failed' for x in records):sys.exit(1)
