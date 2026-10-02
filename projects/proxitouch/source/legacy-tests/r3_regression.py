"""Pixel regression of unrequested pages against the actual R2 offline build.
Set PT_R2_HTML to an original R2 offline HTML when rerunning elsewhere.
"""
from harness import *
from PIL import Image,ImageChops,ImageStat
import json,hashlib,sys
baseline=Path(os.environ.get('PT_R2_HTML','/mnt/data/r3_baseline/dist/ProxiTouch-offline.html'))
if not baseline.exists():raise FileNotFoundError('Set PT_R2_HTML to the original R2 offline HTML')
folder=ROOT/'qa/regression';folder.mkdir(parents=True,exist_ok=True)
items=[(s,p) for s in ['S00','S08','S09','S11','S14','S15','S16','S17','S19','S21'] for p in ([1] if s=='S00' else [.5,1])]
reports={}
with sync_playwright() as p:
 for version,path in [('R2',baseline),('R3',ROOT/'dist/ProxiTouch-offline.html')]:
  b,page,errors=launch(p,html_path=path);page.evaluate('__PT.captureMode(true)')
  diagnostics=[]
  for sid,phase in items:
   page.evaluate('([s,p])=>{__PT.goTo(s,p);__PT.flush()}',[sid,phase]);page.screenshot(path=str(folder/f'{version}-{sid}-{phase}.png'))
   diagnostics.append(page.evaluate('__PT.diagnostics()'));print(version,sid,phase,flush=True)
  reports[version]={'sourceSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'errors':errors,'diagnostics':diagnostics}
  b.close()
results=[]
for sid,phase in items:
 a=Image.open(folder/f'R2-{sid}-{phase}.png').convert('RGB');b=Image.open(folder/f'R3-{sid}-{phase}.png').convert('RGB');d=ImageChops.difference(a,b);stats=ImageStat.Stat(d);hist=d.histogram();neq=sum(1 for px in d.getdata() if max(px)>0)
 results.append({'scene':sid,'phase':phase,'pixelIdentical':not d.getbbox(),'changedPixels':neq,'meanAbsChannelDifference':stats.mean,'differenceBox':d.getbbox(),'maxChannelDelta':max(hi for lo,hi in d.getextrema()),'withinOneLevelSparseRasterTolerance':max(hi for lo,hi in d.getextrema())<=1 and neq<=20})
 if d.getbbox():d.save(folder/f'DIFF-{sid}-{phase}.png')
print('IDENTICAL',sum(x['pixelIdentical'] for x in results),'/',len(results),flush=True)
(folder/'report.json').write_text(json.dumps({'builds':reports,'comparisons':results},ensure_ascii=False,indent=2))
