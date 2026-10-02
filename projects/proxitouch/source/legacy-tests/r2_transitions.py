from harness import *
import json,hashlib,sys
from PIL import Image,ImageDraw
folder=ROOT/'qa/transitions';folder.mkdir(parents=True,exist_ok=True)
ids=sys.argv[1:] or ['S02','S06','S08','S09','S11','S14','S15','S16','S17','S18','S19','S20','S21','S22']
sha=hashlib.sha256((ROOT/'dist/ProxiTouch-offline.html').read_bytes()).hexdigest()
with sync_playwright() as p:
 b,page,errors=launch(p)
 try:
  for sid in ids:
   records=[];frames=[]
   for phase in [0,.25,.5,.75,1]:
    page.evaluate('([s,p])=>window.__PT.goTo(s,p)',[sid,phase]);page.evaluate('window.__PT.flush()')
    name=f'{sid}-{int(phase*100):03}.png';page.screenshot(path=str(folder/name))
    d=page.evaluate('window.__PT.diagnostics()');rect=page.locator('#model-zone').bounding_box();snapshot=page.evaluate('window.__PT.snapshot()')
    records.append({'phase':phase,'file':name,'diagnostic':d,'snapshot':snapshot,'modelRect':rect});frames.append((name,rect,phase));print(sid,phase,d['glError'],d['labelOverlapCount'],flush=True)
    (folder/(sid+'.json')).write_text(json.dumps({'sourceSha256':sha,'errors':errors,'frames':records},ensure_ascii=False,indent=2))
   wall=Image.new('RGB',(1920,1020),'#eef3f7');draw=ImageDraw.Draw(wall)
   for i,(name,rect,phase) in enumerate(frames):
    im=Image.open(folder/name).convert('RGB');crop=im.crop((int(rect['x'])-3,int(rect['y'])-3,int(rect['x']+rect['width'])+3,int(rect['y']+rect['height'])+3));crop.thumbnail((636,466))
    x=i%3*640;y=i//3*510;wall.paste(crop,(x+(640-crop.width)//2,y+40+(466-crop.height)//2));draw.text((x+20,y+15),f'{sid} / {int(phase*100)}%',fill='#284e65')
   wall.save(folder/(sid+'-sheet.png'))
 finally:b.close()
