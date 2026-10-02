from harness import *
import json,sys,hashlib
from PIL import Image,ImageDraw
folder=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'qa/iterations/v3-transitions'
folder.mkdir(parents=True,exist_ok=True)
transitions=[('F01-gap','F01',0,1),('F02-overlap','F02',0,1),('F03-dielectric','F03',0,1),('F05-classics','F05',0,1),('F08-morph','F08',0,1),('F10-approach','F10',0,1),('F13-macro-micro','F13',0,1/3),('F13-micro-nano','F13',1/3,2/3),('F14-EDL-formation','F14',0,1),('F19-pressure','F19',0,1),('D05-explode','D05',0,.6),('D05-reassemble','D05',.8,1),('D12-touch','D12',0,1),('D14-handover','D14',0,1),('D17-release','D17',0,1),('D19-array','D19',0,1),('D21-grasp','D21',0,1),('D22-return','D22',.75,1)]
selected=os.environ.get("PT_TRANSITIONS","").split(",")
if selected!=[""]: transitions=[t for t in transitions if t[0] in selected]
report=[]
with sync_playwright() as p:
 b,page,errors=launch(p)
 page.evaluate('window.__PT.captureMode(true)')
 try:
  for name,scene,a,z in transitions:
   sheet=Image.new('RGB',(1800,1596),'#eff4f7');draw=ImageDraw.Draw(sheet)
   for i,t in enumerate([0,.25,.5,.75,1]):
    phase=a+(z-a)*t;path=folder/f'{name}-{int(t*100):03}.png'
    page.evaluate('([s,t])=>window.__PT.goTo(s,t)',[scene,phase]);page.wait_for_timeout(350);page.evaluate('window.__PT.flush()');page.screenshot(path=str(path))
    diag=page.evaluate('window.__PT.diagnostics()');diag.update({'transition':name,'fraction':t,'capture':path.name});report.append(diag)
    im=Image.open(path).convert('RGB').resize((900,506));xx=(i%2)*900;yy=(i//2)*532;sheet.paste(im,(xx,yy+26));draw.text((xx+15,yy+7),f'{name}  {int(t*100)}%  scene phase {phase:.5f}',fill='#224255')
    print(name,t,'GL',diag['glError'],'overlaps',diag['overlayOverlapPairs'],diag['labelOverlapCount'],flush=True)
   sheet.save(folder/f'{name}-sheet.png')
   (folder/'report.json').write_text(json.dumps({'sourceSha256':hashlib.sha256((ROOT/'dist/ProxiTouch-offline.html').read_bytes()).hexdigest(),'errors':errors,'captures':report},ensure_ascii=False,indent=2))
 finally:b.close()
print('DONE',len(report),flush=True)
