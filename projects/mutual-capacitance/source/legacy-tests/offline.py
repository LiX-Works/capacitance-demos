from harness import *
import json,hashlib,subprocess,time,urllib.request,sys
R=ROOT/'qa/offline';R.mkdir(parents=True,exist_ok=True)
sha=hashlib.sha256((ROOT/'dist/Capacitance-Lab-offline.html').read_bytes()).hexdigest();report={'sourceSha256':sha,'navigation':[],'coldOffline':{},'http':[]}
server=subprocess.Popen(['node','scripts/serve.mjs'],cwd=ROOT/'source',env={**os.environ,'PORT':'4178'},stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
time.sleep(.5)
try:
 for path in ['/','/app.js','/style.css','/Capacitance-Lab-offline.html','/js/main.js']:
  with urllib.request.urlopen('http://127.0.0.1:4178'+path,timeout=10) as r:body=r.read();report['http'].append({'path':path,'status':r.status,'bytes':len(body)})
 with sync_playwright() as p:
  browser,page,initial_errors=launch(p);page.close()
  for kind,url in [('file',(ROOT/'dist/Capacitance-Lab-offline.html').as_uri()),('http','http://127.0.0.1:4178/')]:
   page=browser.new_page(viewport={'width':1920,'height':1080});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   item={'kind':kind,'url':url,'loaded':False,'errors':errors}
   try:
    page.goto(url,wait_until='load',timeout=25000);page.wait_for_function('window.__LAB?.ready',timeout=10000);page.evaluate('__LAB.goTo("02",1);__LAB.captureMode(true);__LAB.flush()');page.screenshot(path=str(R/(kind+'-entry.png')));item.update({'loaded':True,'diagnostic':page.evaluate('__LAB.diagnostics()')})
   except Exception as exc:item['failure']=str(exc)
   finally:page.close();report['navigation'].append(item)
  context=browser.new_context(offline=True,viewport={'width':1920,'height':1080});page=context.new_page();requests=[];errors=[];page.on('request',lambda r:requests.append(r.url));page.on('pageerror',lambda e:errors.append(str(e)))
  page.set_content((ROOT/'dist/Capacitance-Lab-offline.html').read_text(),wait_until='load',timeout=60000);page.wait_for_function('__LAB.ready',timeout=10000);page.evaluate('__LAB.goTo("09",1);__LAB.captureMode(true);__LAB.flush()');page.screenshot(path=str(R/'cold-offline-field.png'));report['coldOffline']={'loaded':True,'requests':requests,'errors':errors,'diagnostics':page.evaluate('__LAB.diagnostics()')}
  page.evaluate('__LAB.captureMode(false)');button=page.locator('#fullscreen');
  try:
   button.click(timeout=5000);page.wait_for_timeout(150);report['fullscreen']={'active':page.evaluate('!!document.fullscreenElement'),'bodyEnd':page.locator('body').inner_text()[-600:]}
  except Exception as exc:report['fullscreen']={'active':False,'error':str(exc)}
  report['noPolicyChangesMade']=True;browser.close()
finally:server.terminate();server.wait(timeout=5)
(R/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2)[:4500],flush=True)
assert report['coldOffline']['loaded'] and not report['coldOffline']['requests'] and not report['coldOffline']['errors']
