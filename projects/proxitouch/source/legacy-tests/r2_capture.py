from harness import *
import json,hashlib,sys
from PIL import Image,ImageDraw
folder=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'qa/captures/1920x1080'
width=int(os.environ.get('PT_WIDTH','1920'));height=int(width*9/16)
folder.mkdir(parents=True,exist_ok=True);report=[]
sha=hashlib.sha256((ROOT/'dist/ProxiTouch-offline.html').read_bytes()).hexdigest()
with sync_playwright() as p:
 b,page,errors=launch(p,width,height)
 try:
  ids=page.evaluate('window.__PT.scenes.map(s=>s.id)')
  if os.environ.get('PT_IDS'):ids=os.environ['PT_IDS'].split(',')
  for sid in ids:
   page.evaluate('s=>window.__PT.goTo(s,1)',sid);page.evaluate('window.__PT.flush()');page.screenshot(path=str(folder/(sid+'.png')))
   d=page.evaluate('window.__PT.diagnostics()');d['sourceSha256']=sha;report.append(d)
   (folder/('diagnostic-'+sid+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2))
   print(sid,d['glError'],d['overflow'],d['labelOverlapCount'],d['mathErrors'],flush=True)
  (folder/('batch-'+ids[0]+'.json')).write_text(json.dumps({'sourceSha256':sha,'width':width,'height':height,'errors':errors,'captures':report},ensure_ascii=False,indent=2))
 finally:b.close()
for start in range(0,len(ids),4):
 wall=Image.new('RGB',(1920,1128),'#eef3f7');draw=ImageDraw.Draw(wall)
 for j,sid in enumerate(ids[start:start+4]):
  im=Image.open(folder/(sid+'.png')).convert('RGB').resize((960,540));x=j%2*960;y=j//2*564;wall.paste(im,(x,y+24));draw.text((x+12,y+5),sid,fill='#244d65')
 wall.save(folder/(ids[start]+'-'+ids[min(start+3,len(ids)-1)]+'-sheet.png'))
