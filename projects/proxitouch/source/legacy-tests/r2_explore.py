from harness import *
import json,hashlib,sys
from PIL import Image,ImageDraw
views=sys.argv[1:] or ['device','field','micro','nano','signal','exploded']
folder=ROOT/'qa/explore';folder.mkdir(parents=True,exist_ok=True)
sha=hashlib.sha256((ROOT/'dist/ProxiTouch-offline.html').read_bytes()).hexdigest()
width=int(os.environ.get('PT_WIDTH','1920'));height=int(width*9/16)
with sync_playwright() as p:
 b,page,errors=launch(p,width,height)
 try:
  page.evaluate("window.__PT.goTo('S19',.55)");before=page.evaluate('window.__PT.snapshot()');page.keyboard.press('e')
  for view in views:
   page.locator('[data-view="'+view+'"]').click();records=[]
   for depth in [-.6,.025,.7]:
    page.locator('#depth-input').fill(str(depth));page.locator('#depth-input').dispatch_event('input');page.evaluate('window.__PT.flush()')
    name=f'{width}-{view}-{depth}.png';page.screenshot(path=str(folder/name));d=page.evaluate('window.__PT.diagnostics()');s=page.evaluate('window.__PT.snapshot()')
    records.append({'file':name,'depth':depth,'snapshot':s,'diagnostic':d});print(view,depth,d['glError'],d['overflow'],d['labelOverlapCount'],flush=True)
    (folder/f'{width}-{view}.json').write_text(json.dumps({'sourceSha256':sha,'errors':errors,'states':records},ensure_ascii=False,indent=2))
   wall=Image.new('RGB',(1920,390),'#eef3f7');dr=ImageDraw.Draw(wall)
   for i,r in enumerate(records):
    im=Image.open(folder/r['file']).convert('RGB').resize((640,360));wall.paste(im,(640*i,30));dr.text((640*i+12,8),f'{view} / depth {r["depth"]}',fill='#244b65')
   wall.save(folder/f'{width}-{view}-sheet.png')
  page.keyboard.press('Escape');after=page.evaluate('window.__PT.snapshot()')
  (folder/f'{width}-return-{views[0]}.json').write_text(json.dumps({'sourceSha256':sha,'restored':all(before[k]==after[k] for k in ['scene','phase','model','camera','notes']),'before':before,'after':after,'errors':errors},ensure_ascii=False,indent=2))
 finally:b.close()
