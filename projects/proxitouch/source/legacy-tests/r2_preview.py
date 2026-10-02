from harness import *
import json,sys
from PIL import Image,ImageDraw
folder=ROOT/'qa/iterations/first';folder.mkdir(parents=True,exist_ok=True)
ids=sys.argv[1:] or ['S01','S06','S09','S11','S14','S18','S20','S22']
report=[]
with sync_playwright() as p:
 b,page,errors=launch(p)
 try:
  for sid in ids:
   page.evaluate('s=>window.__PT.goTo(s,1)',sid);page.wait_for_timeout(150);page.evaluate('window.__PT.flush()');page.screenshot(path=str(folder/(sid+'.png')))
   d=page.evaluate('window.__PT.diagnostics()');report.append(d);print(sid,d['glError'],d['overflow'],d['labelOverlapCount'],d['mathErrors'],d['subjectBounds'],flush=True)
  (folder/'report.json').write_text(json.dumps({'errors':errors,'scenes':report},ensure_ascii=False,indent=2))
 finally:b.close()
wall=Image.new('RGB',(1600,480*((len(ids)+1)//2)), '#eef3f7');draw=ImageDraw.Draw(wall)
for i,sid in enumerate(ids):
 im=Image.open(folder/(sid+'.png')).convert('RGB');im.thumbnail((800,450));x=i%2*800;y=i//2*480;wall.paste(im,(x,y+28));draw.text((x+12,y+8),sid,fill='#244d65')
wall.save(folder/'wall.png')
