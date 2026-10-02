from harness import *
os.environ["PT_OFFLINE_BROWSER"]="1"
import json,hashlib
out=ROOT/'qa/extras';out.mkdir(parents=True,exist_ok=True);captures=[];checks=[]
with sync_playwright() as p:
 b,page,errors=launch(p)
 page.evaluate('window.__PT.captureMode(true)')
 for scene in ['F14','D16']:
  page.evaluate('(s)=>{window.__PT.goTo(s,.72);window.__PT.quality("high")}',scene)
  before=page.evaluate('window.__PT.snapshot().model')
  page.evaluate('window.__PT.quality("safe")');page.wait_for_timeout(300);page.evaluate('window.__PT.flush()');page.screenshot(path=str(out/('safe-'+scene+'.png')))
  captures.append({'capture':'safe-'+scene+'.png',**page.evaluate('window.__PT.diagnostics()')});checks.append({'name':'Safe preserves full scientific model '+scene,'pass':before==page.evaluate('window.__PT.snapshot().model')})
 page.evaluate('window.__PT.quality("high")');page.set_viewport_size({'width':1366,'height':768});page.wait_for_timeout(200)
 for scene in ['F16','D16']:
  page.evaluate('(s)=>window.__PT.goTo(s,1)',scene);page.wait_for_timeout(300);page.evaluate('window.__PT.flush()');name='1366-'+scene+'.png';page.screenshot(path=str(out/name));captures.append({'capture':name,**page.evaluate('window.__PT.diagnostics()')})
 checks.append({'name':'All extra captured layouts are bounded and free of runtime / GL / math errors','pass':all(not c['overflow'] and not c['documentOverflow'] and not c['overlayOverlapPairs'] and c['labelOverlapCount']==0 and c['labelOutOfBounds']==0 and c['mathErrors']==0 and c['glError']==0 for c in captures) and not errors})
 requests=page.pt_requests;checks.append({'name':'Cold offline context loads the application without external resource requests','pass':os.environ.get('PT_OFFLINE_BROWSER')=='1' and not requests,'detail':requests})
 b.close()
(out/'report.json').write_text(json.dumps({'sourceSha256':hashlib.sha256((ROOT/'dist/ProxiTouch-offline.html').read_bytes()).hexdigest(),'coldOfflineContext':os.environ.get('PT_OFFLINE_BROWSER')=='1','requests':requests,'checks':checks,'captures':captures,'errors':errors},ensure_ascii=False,indent=2))
print('DONE',len(captures),checks,flush=True)
