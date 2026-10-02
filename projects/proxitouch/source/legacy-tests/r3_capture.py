"""Deterministic real Chromium screenshots, explicit main and ambient clocks."""
from harness import *
import json,hashlib,sys,time
ROOTQA=ROOT/'qa'
width=int(os.environ.get('PT_WIDTH','1920'));height=width*9//16
mode=sys.argv[1] if len(sys.argv)>1 else 'scenes'
out=ROOTQA/mode/f'{width}x{height}';out.mkdir(parents=True,exist_ok=True)
sha=hashlib.sha256((ROOT/'dist/ProxiTouch-offline.html').read_bytes()).hexdigest()
items=[]
if mode=='scenes':
 for i in range(23):
  sid=f'S{i:02}';items.append((sid,1,{'S05':5.2,'S07':1.7,'S10':1.5}.get(sid,0),None,None,sid))
elif mode=='transitions':
 for sid in ['S01','S02','S03','S04','S06','S10','S22']:
  for t in [0,.25,.5,.75,1]:items.append((sid,t,0,None,None,f'{sid}-{round(t*100):03}'))
 for sid,values in [('S12',[.9,.95,.98,.995,1]),('S13',[0,.005,.02,.05,.1,.25,.5,.75,1]),('S20',[0,.115,.23,.30,.34,.4,.45,.5,.56,.61,.66,.71,.715,.72,.78,.85,.94,1])]:
  for t in values:items.append((sid,t,0,None,None,f'{sid}-{round(t*1000):04}'))
 for t in [.46,.62,.80,.92]:items.append(('S22',t,0,None,None,f'S22-{round(t*1000):04}'))
elif mode=='ambient':
 for sid,values in [('S05',[0,1.7,2.5,4.25,5.2,6.5,7.2]),('S07',[0,2,4,6,8]),('S10',[0,1.45,2.9,4.35,5.8]),('S18',[0,.76,.88,1,1.5,1.88,2])]:
  for a in values:items.append((sid,1,a,None,None,f'{sid}-a{a:.2f}'.replace('.','p')))
elif mode=='explore':
 for view in ['device','field','micro','nano','signal','exploded']:
  for depth in [-.4,.7]:items.append(('S19',.7,0,view,depth,f'{view}-depth{depth}'.replace('.','p')))
else:raise ValueError(mode)
records=[]
with sync_playwright() as p:
 b,page,errors=launch(p,width,height)
 page.set_default_timeout(20000)
 page.evaluate('__PT.captureMode(true)')
 for sid,t,a,view,depth,name in items:
  begin=time.monotonic()
  page.evaluate('([s,p,a,v,d])=>{__PT.app.captureAmbient=a;__PT.goTo(s,p);if(v){__PT.view(v);__PT.setDepth(d);}__PT.flush();}',[sid,t,a,view,depth])
  page.screenshot(path=str(out/(name+'.png')),timeout=60000)
  diag=page.evaluate('__PT.diagnostics()');snap=page.evaluate('__PT.snapshot()')
  failed=bool(diag['glError'] or diag['overflow'] or diag['documentOverflow'] or diag['labelOverlapCount'] or diag['labelOutOfBounds'] or diag['mathErrors'] or diag['overlayOverlapPairs'] or diag['errors'])
  rec={'file':name+'.png','phase':t,'ambientSeconds':a,'passed':not failed,'diagnostic':diag,'snapshot':snap};records.append(rec)
  report={'sourceSha256':sha,'mode':mode,'width':width,'height':height,'errors':errors,'requests':page.pt_requests,'captures':records}
  (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
  print('FAIL' if failed else 'PASS',name,'sec',round(time.monotonic()-begin,1),flush=True)
 b.close()
if errors or any(not r['passed'] for r in records):sys.exit(1)
