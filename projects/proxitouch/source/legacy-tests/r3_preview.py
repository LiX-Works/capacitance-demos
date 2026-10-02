from harness import launch,ROOT
from playwright.sync_api import sync_playwright
import json,time,sys
out=ROOT/'qa/iterations/initial';out.mkdir(parents=True,exist_ok=True)
items=[('S01',1,0),('S02',1,0),('S03',1,0),('S04',1,0),('S05',1,2.5),('S05',1,5.2),('S06',.5,0),('S07',1,1.7),('S10',.4,0),('S10',.7,0),('S10',1,1.5),('S12',1,0),('S13',0,0),('S18',1,0),('S18',1,1.2),('S20',.45,0),('S22',0,0),('S22',.6,0),('S22',1,0)]
if len(sys.argv)>1:items=[x for x in items if x[0] in sys.argv[1:]]
records=[]
with sync_playwright() as p:
 browser,page,errors=launch(p)
 page.evaluate('window.__PT.captureMode(true)')
 for scene,phase,ambient in items:
  start=time.monotonic()
  page.evaluate('([s,p,t])=>{__PT.goTo(s,p);__PT.ambientTime(t);__PT.flush();}',[scene,phase,ambient])
  name=f'{scene}-{phase:.2f}-a{ambient:.1f}'.replace('.','p')
  page.screenshot(path=str(out/(name+'.png')),timeout=60000)
  d=page.evaluate('__PT.diagnostics()');records.append({'file':name,**d})
  print(name,'sec',round(time.monotonic()-start,1),'draw',d['drawCalls'],'tri',d['triangles'],'labels',d['labelOverlapCount'],'app',d['geometry']['application'],flush=True)
 browser.close()
(out/'diagnostics.json').write_text(json.dumps({'records':records,'errors':errors},ensure_ascii=False,indent=2))
print('ERRORS',errors)
