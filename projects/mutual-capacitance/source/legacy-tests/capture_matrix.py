from harness import *
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,os,sys
SHA=hashlib.sha256((ROOT/'dist/Capacitance-Lab-offline.html').read_bytes()).hexdigest()
mode=os.environ.get('MODE','final');widths=[int(os.environ['WIDTH'])]if os.environ.get('WIDTH')else[1920,2560]
records=[]
def sheet(paths,name,tile=800,cols=3):
 h=tile*9//16+26;im=Image.new('RGB',(tile*cols,((len(paths)+cols-1)//cols)*h),'#eef4f8');d=ImageDraw.Draw(im)
 for i,p in enumerate(paths):x=i%cols*tile;y=i//cols*h;im.paste(Image.open(p).convert('RGB').resize((tile,h-26)),(x,y+26));d.text((x+12,y+6),p.stem,fill='#234c66')
 im.save(name)
with sync_playwright() as p:
 for w in widths:
  out=ROOT/f'qa/{mode}/{w}';out.mkdir(parents=True,exist_ok=True)
  b,page,errors=launch(p,w,w*9//16);page.evaluate('__LAB.captureMode(true)')
  try:
   for i in range(12):
    sid=f'{i+1:02d}';paths=[]
    phases=[1]if mode=='final'else[0,.25,.5,.75,1]
    for t in phases:
     page.evaluate('(a)=>{__LAB.goTo(a[0],a[1]);__LAB.flush()}',[sid,t]);fn=out/f'{sid}-{int(t*100):03d}.png';page.screenshot(path=str(fn));paths.append(fn)
     d=page.evaluate('''()=>{const d=__LAB.diagnostics();d.formulaOverflow=document.querySelector('.formula').scrollWidth>document.querySelector('.formula').clientWidth+2;return d}''')
     records.append({'file':str(fn.relative_to(ROOT/'qa')),'sourceSha256':SHA,**d});print(w,sid,t,d['glError'],d['overflow'],d['labelOverlaps'],d['mathErrors'],'formula',d['formulaOverflow'],flush=True)
    if mode!='final':sheet(paths,out/f'{sid}-review.png',640,3)
   if mode=='final':
    for st in range(0,12,4):sheet([out/f'{i+1:02d}-100.png'for i in range(st,st+4)],out/f'review-{st//4+1}.png',960,2)
  finally:b.close()
  (out/'report.json').write_text(json.dumps({'sourceSha256':SHA,'records':[x for x in records if x['file'].startswith(f'{mode}/{w}/')],'errors':errors},ensure_ascii=False,indent=2))
  if errors:raise RuntimeError(str(errors))
if any(r['glError']or r['overflow']or r['labelOverlaps']or r['mathErrors']or r['documentOverflow']or r['formulaOverflow']for r in records):sys.exit(1)
